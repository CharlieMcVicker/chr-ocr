"""
Staged Epoch Loop supervisor script for dynamic augmentation generation and Tesseract model training.
Orchestrates Tesseract training epoch-by-epoch while maintaining a low disk footprint.
"""

import os
import sys
import glob
import subprocess
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from phoenix.config import TrainingConfig

def download_file(url, dest):
    """
    Downloads a file from url to dest with progress printing.
    """
    print(f"Downloading {url} to {dest}...")
    urllib.request.urlretrieve(url, dest)

def get_latest_checkpoint(checkpoint_dir):
    """
    Scans the checkpoint directory and returns the path to the most recent checkpoint file.
    """
    checkpoints = glob.glob(os.path.join(checkpoint_dir, "*.checkpoint"))
    if not checkpoints:
        return None
    # Sort by modification time
    checkpoints.sort(key=os.path.getmtime)
    return checkpoints[-1]

def compile_image(img_path, model_dir):
    """
    Compiles a single PNG image to .lstmf using tesseract.
    """
    base = os.path.splitext(img_path)[0]
    # Find the correct path of lstm.train inside homebrew directory
    lstm_train_config = "/opt/homebrew/share/tessdata/configs/lstm.train"
    if not os.path.exists(lstm_train_config):
        # fallback to Cellar path
        import glob
        matches = glob.glob("/opt/homebrew/Cellar/tesseract/*/share/tessdata/configs/lstm.train")
        if matches:
            lstm_train_config = matches[0]

    subprocess.run(
        ["tesseract", img_path, base, "--tessdata-dir", model_dir, "-l", "chr", "--oem", "1", "--psm", "13", lstm_train_config],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    return os.path.abspath(base + ".lstmf")

def run_staged_training(config: TrainingConfig):
    """
    Runs the Staged Epoch Loop for Tesseract OCR fine-tuning.
    """
    # 1. Directories setup
    os.makedirs(config.model_dir, exist_ok=True)
    os.makedirs(config.train_output_dir, exist_ok=True)

    # 2. Download and extract base models if needed
    traineddata_path = os.path.join(config.model_dir, "chr.traineddata")
    if not os.path.exists(traineddata_path):
        url = "https://github.com/tesseract-ocr/tessdata_best/raw/main/chr.traineddata"
        download_file(url, traineddata_path)

    base_lstm_path = os.path.join(config.model_dir, "chr.lstm")
    if not os.path.exists(base_lstm_path):
        print("Extracting base lstm model from chr.traineddata...")
        # Runs combine_tessdata -u model_dir/chr.traineddata model_dir/chr.
        subprocess.run(
            ["combine_tessdata", "-u", "chr.traineddata", "chr."],
            cwd=config.model_dir,
            check=True
        )

    # 3. Main Staged Epoch Loop
    print(f"\n=== Starting Staged Epoch Loop: {config.total_epochs} epochs, {config.iterations_per_epoch} iterations per epoch ===")
    
    for epoch in range(1, config.total_epochs + 1):
        print(f"\n--- Epoch {epoch}/{config.total_epochs} ---")
        
        # Step A: Clean and recreate temporary epoch directory
        if os.path.exists(config.output_dir):
            shutil.rmtree(config.output_dir)
        os.makedirs(config.output_dir, exist_ok=True)

        # Step B: Generate fresh random dynamic augmentations (only train split)
        manifest_to_use = config.train_manifest
        if config.use_dynamic_cnt:
            import json
            import random
            
            print(f"Generating dynamic mixed manifest for epoch {epoch}...")
            if not os.path.exists(config.train_manifest):
                raise FileNotFoundError(f"Base manifest not found: {config.train_manifest}")
            
            with open(config.train_manifest, "r", encoding="utf-8") as f:
                base_data = json.load(f)
            
            # Filter out any existing CNT items to keep the Phoenix base clean
            mixed_data = {
                k: v for k, v in base_data.items()
                if v.get("dataset") != "cnt"
            }
            
            # Assign split stable logic to Phoenix Cherokee items (same as mix_datasets.py)
            labeled_phoenix_items = [
                item for item in mixed_data.values()
                if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
            ]
            
            # If split is not set, set it stably
            phoenix_split = 0.8
            accumulator = 0.0
            for item in labeled_phoenix_items:
                if "split" not in item:
                    accumulator += (1.0 - phoenix_split)
                    if accumulator >= 1.0:
                        item["split"] = "test"
                        accumulator -= 1.0
                    else:
                        item["split"] = "train"
            
            # Get the exact list of Phoenix training items
            phoenix_train_items = [
                item for item in labeled_phoenix_items
                if item.get("split") == "train"
            ]
            n_phoenix = len(phoenix_train_items)
            
            # Calculate required CNT lines based on mixture_ratio
            if config.mixture_ratio <= 0.0 or config.mixture_ratio >= 1.0:
                raise ValueError(f"mixture_ratio must be between 0 and 1, got {config.mixture_ratio}")
            
            n_cnt = int(n_phoenix * (1.0 - config.mixture_ratio) / config.mixture_ratio)
            print(f"Computed batch mixture: Phoenix train samples = {n_phoenix}, target CNT samples = {n_cnt} (ratio = {config.mixture_ratio:.2f})")
            
            # Now, gather all valid CNT lines across all books
            all_valid_cnt_lines = []
            for book_idx in range(1, 28):
                book_dir = os.path.join(config.cnt_dir, f"book_{book_idx:02d}")
                cnt_manifest_path = os.path.join(book_dir, "aligned_manifest.json")
                if not os.path.exists(cnt_manifest_path):
                    continue
                
                with open(cnt_manifest_path, "r", encoding="utf-8") as f:
                    aligned_manifest = json.load(f)
                
                for verse_key in sorted(aligned_manifest.keys()):
                    verse = aligned_manifest[verse_key]
                    for line_idx, line in enumerate(verse.get("lines", [])):
                        ftm_aligned = line.get("ftm_aligned", "").strip()
                        if ftm_aligned:
                            all_valid_cnt_lines.append({
                                "book_idx": book_idx,
                                "verse_key": verse_key,
                                "line_idx": line_idx,
                                "line": line
                            })
            
            # Load rare characters list
            rare_chars = set()
            rare_chars_path = "training_data/rare_characters.json"
            if os.path.exists(rare_chars_path):
                try:
                    with open(rare_chars_path, "r", encoding="utf-8") as f:
                        rare_chars = set(json.load(f))
                    print(f"Loaded {len(rare_chars)} rare characters for CNT oversampling.")
                except Exception as e:
                    print(f"Warning: Failed to load rare characters: {e}")

            # Seeding with epoch ensures a different but deterministic subset per epoch
            seed_str = f"cnt_batch_salt_epoch_{epoch}"
            rng = random.Random(seed_str)
            
            if n_cnt > 0 and len(all_valid_cnt_lines) > 0:
                # Separate CNT lines into those containing rare characters and those that don't
                rare_cnt_lines = []
                common_cnt_lines = []
                for x in all_valid_cnt_lines:
                    text = x["line"].get("ftm_aligned", "")
                    if any(c in text for c in rare_chars):
                        rare_cnt_lines.append(x)
                    else:
                        common_cnt_lines.append(x)

                print(f"CNT Lines breakdown: {len(rare_cnt_lines)} with rare characters, {len(common_cnt_lines)} with common characters.")

                # Sample exactly n_cnt lines (cap to size of all_valid_cnt_lines if needed)
                sampled_count = min(n_cnt, len(all_valid_cnt_lines))

                # Shuffle both groups using rng
                rng.shuffle(rare_cnt_lines)
                rng.shuffle(common_cnt_lines)

                # Prioritize rare CNT lines first, then fill with common CNT lines
                if len(rare_cnt_lines) >= sampled_count:
                    sampled_lines = rare_cnt_lines[:sampled_count]
                else:
                    needed = sampled_count - len(rare_cnt_lines)
                    sampled_lines = rare_cnt_lines + common_cnt_lines[:needed]

                print(f"Sampled {len(sampled_lines)} total CNT lines (including {min(len(rare_cnt_lines), sampled_count)} rare lines).")
                
                for item_info in sampled_lines:
                    book_idx = item_info["book_idx"]
                    verse_key = item_info["verse_key"]
                    line_idx = item_info["line_idx"]
                    line = item_info["line"]
                    
                    item_id = f"cnt_{book_idx:02d}_{verse_key}_line_{line_idx:02d}"
                    image_path = f"cnt/book_{book_idx:02d}/line_crops/{verse_key}_line_{line_idx:02d}.png"
                    
                    # Note: All dynamic CNT samples are train items for this epoch's training run
                    mixed_data[item_id] = {
                        "id": item_id,
                        "image_path": image_path,
                        "label": line["ftm_aligned"],
                        "status": "labeled",
                        "predicted_lang": "Cherokee",
                        "dataset": "cnt",
                        "split": "train"
                    }
                total_cnt_sampled = len(sampled_lines)
            else:
                total_cnt_sampled = 0
            
            # Enforce that only train items (Phoenix train + CNT sampled train) are kept in the training set
            # The test items should not be augmented or trained on in this epoch
            epoch_data = {}
            for k, v in mixed_data.items():
                if v.get("split") == "train":
                    epoch_data[k] = v
                elif v.get("split") == "test":
                    # Keep test items in manifest if they are needed for reference, but train listfile will only compile train items
                    epoch_data[k] = v
            
            manifest_to_use = os.path.join(config.output_dir, f"manifest_epoch_{epoch}.json")
            with open(manifest_to_use, "w", encoding="utf-8") as f:
                json.dump(epoch_data, f, ensure_ascii=False, indent=2)
            
            # Verify exact ratio of Phoenix to CNT lines in the train set
            train_phoenix_count = sum(1 for item in epoch_data.values() if item.get("split") == "train" and item.get("dataset") != "cnt")
            train_cnt_count = sum(1 for item in epoch_data.values() if item.get("split") == "train" and item.get("dataset") == "cnt")
            actual_ratio = train_phoenix_count / (train_phoenix_count + train_cnt_count) if (train_phoenix_count + train_cnt_count) > 0 else 0.0
            print(f"Generated epoch {epoch} manifest at {manifest_to_use}")
            print(f"Train set: {train_phoenix_count} Phoenix lines, {train_cnt_count} CNT lines. Actual Phoenix Ratio: {actual_ratio:.4f} (Target: {config.mixture_ratio:.4f})")
            
        cmd_aug = [
            sys.executable,
            "-u",
            "scripts/augment_dynamic.py",
            "--manifest", manifest_to_use,
            "--output-dir", config.output_dir,
            "--variations-per-image", str(config.variations_per_image),
            "--error-rate", str(config.error_rate),
            "--blur-prob", str(config.blur_prob),
            "--shadow-prob", str(config.shadow_prob),
            "--distortion-prob", str(config.distortion_prob),
            "--dropout-prob", str(config.dropout_prob),
            "--bleedthrough-prob", str(config.bleedthrough_prob),
            "--distortion-limit", str(config.distortion_limit),
            "--cnt-blur-prob", str(config.cnt_noise["blur"]["prob"]),
            "--cnt-shadow-prob", str(config.cnt_noise["shadow"]["prob"]),
            "--cnt-distortion-prob", str(config.cnt_noise["distortion"]["prob"]),
            "--cnt-dropout-prob", str(config.cnt_noise["dropout"]["prob"]),
            "--cnt-blur-limit-min", str(config.cnt_noise["blur"]["limit_min"]),
            "--cnt-blur-limit-max", str(config.cnt_noise["blur"]["limit_max"]),
            "--cnt-shadow-dimension", str(config.cnt_noise["shadow"]["dimension"]),
            "--cnt-distortion-limit", str(config.cnt_noise["distortion"]["limit"]),
            "--cnt-dropout-holes-min", str(config.cnt_noise["dropout"]["holes_min"]),
            "--cnt-dropout-holes-max", str(config.cnt_noise["dropout"]["holes_max"]),
            "--cnt-dropout-size-min", str(config.cnt_noise["dropout"]["size_min"]),
            "--cnt-dropout-size-max", str(config.cnt_noise["dropout"]["size_max"])
        ]
        subprocess.run(cmd_aug, check=True)

        # Step C: Compile augmented images to .lstmf files and create list.train
        print("Compiling images to .lstmf files...")
        png_files = glob.glob(os.path.join(config.output_dir, "*.png"))
        if not png_files:
            raise RuntimeError("Error: No augmented PNGs generated!")

        list_train_path = os.path.join(config.output_dir, "list.train")
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            lstmf_paths = list(executor.map(lambda f: compile_image(f, config.model_dir), png_files))

        with open(list_train_path, "w", encoding="utf-8") as list_f:
            for lstmf_path in lstmf_paths:
                list_f.write(lstmf_path + "\n")

        # Step D: Determine continue_from model checkpoint
        continue_model = None
        if epoch == 1:
            if config.continue_from:
                continue_model = config.continue_from
            else:
                # Check if there is an existing checkpoint in train_output_dir
                latest = get_latest_checkpoint(config.train_output_dir)
                if latest:
                    continue_model = latest
                else:
                    continue_model = base_lstm_path
        else:
            latest = get_latest_checkpoint(config.train_output_dir)
            if latest:
                continue_model = latest
            else:
                print("Warning: No checkpoint found from previous epoch! Falling back to base model.", file=sys.stderr)
                continue_model = base_lstm_path

        # Determine current learning rate based on schedule
        current_lr = config.learning_rate
        if config.lr_schedule == "step":
            decay_steps = (epoch - 1) // config.lr_decay_epochs
            current_lr = config.learning_rate * (config.lr_decay_rate ** decay_steps)
        elif config.lr_schedule == "exp":
            current_lr = config.learning_rate * (config.lr_decay_rate ** (epoch - 1))
            
        print(f"Continuing training from: {continue_model}")
        print(f"Current Epoch {epoch} Learning Rate: {current_lr:.8f} (schedule: {config.lr_schedule})")

        # Step E: Run lstmtraining
        # max_iterations grows cumulative-wise for continuing training
        max_iterations = epoch * config.iterations_per_epoch
        print(f"Running lstmtraining for up to {max_iterations} total iterations...")
        
        log_file_path = os.path.join(config.train_output_dir, f"epoch_{epoch}_training.log")
        
        cmd_train = [
            "lstmtraining",
            "--continue_from", continue_model,
            "--model_output", os.path.join(config.train_output_dir, "chr"),
            "--traineddata", traineddata_path,
            "--train_listfile", list_train_path,
            "--max_iterations", str(max_iterations),
            "--learning_rate", str(current_lr)
        ]
        if config.old_traineddata:
            cmd_train.extend(["--old_traineddata", config.old_traineddata])
            
        if current_lr != 0.001:
            cmd_train.append("--reset_learning_rate")
        
        with open(log_file_path, "w", encoding="utf-8") as log_f:
            subprocess.run(cmd_train, stdout=log_f, stderr=subprocess.STDOUT, check=True)

        print(f"Epoch {epoch} training complete! Log written to: {log_file_path}")

        # Step F: Clean up temporary epoch augmented images and .lstmf files to preserve disk space
        print(f"Cleaning up temporary epoch files in {config.output_dir}...")
        # Save manifest_epoch_{epoch}.json to train_output_dir for verification
        if config.use_dynamic_cnt:
            shutil.copy2(manifest_to_use, os.path.join(config.train_output_dir, f"manifest_epoch_{epoch}.json"))
        shutil.rmtree(config.output_dir)

    print("\n=== Staged Epoch Loop finished successfully! ===")
    print(f"Final checkpoints and epoch training logs are in: {config.train_output_dir}")
