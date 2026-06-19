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

        # Step B & C: Generate and compile train inputs
        list_train_path = os.path.join(config.output_dir, "list.train")
        if config.use_shared_pool:
            master_pool_dir = f"training_data/staged_tuning/master_pool_epoch_{epoch}"
            master_index_path = os.path.join(master_pool_dir, "metadata_index.json")
            
            if not os.path.exists(master_index_path):
                print(f"Master pool index not found. Generating master pool for epoch {epoch} at {master_pool_dir}...")
                os.makedirs(master_pool_dir, exist_ok=True)
                
                import json
                if not os.path.exists(config.train_manifest):
                    raise FileNotFoundError(f"Base manifest not found: {config.train_manifest}")
                
                with open(config.train_manifest, "r", encoding="utf-8") as f:
                    base_data = json.load(f)
                
                mixed_data = {
                    k: v for k, v in base_data.items()
                    if v.get("dataset") != "cnt"
                }
                
                labeled_phoenix_items = [
                    item for item in mixed_data.values()
                    if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
                ]
                
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
                
                phoenix_train_items = [
                    item for item in labeled_phoenix_items
                    if item.get("split") == "train"
                ]
                
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
                
                epoch_data = {}
                for item in phoenix_train_items:
                    epoch_data[item["id"]] = item
                
                for item_info in all_valid_cnt_lines:
                    book_idx = item_info["book_idx"]
                    verse_key = item_info["verse_key"]
                    line_idx = item_info["line_idx"]
                    line = item_info["line"]
                    
                    item_id = f"cnt_{book_idx:02d}_{verse_key}_line_{line_idx:02d}"
                    image_path = f"cnt/book_{book_idx:02d}/line_crops/{verse_key}_line_{line_idx:02d}.png"
                    
                    epoch_data[item_id] = {
                        "id": item_id,
                        "image_path": image_path,
                        "label": line["ftm_aligned"],
                        "status": "labeled",
                        "predicted_lang": "Cherokee",
                        "dataset": "cnt",
                        "split": "train"
                    }
                
                master_manifest_to_use = os.path.join(master_pool_dir, f"master_manifest_epoch_{epoch}.json")
                with open(master_manifest_to_use, "w", encoding="utf-8") as f:
                    json.dump(epoch_data, f, ensure_ascii=False, indent=2)
                
                print(f"Generated master manifest with {len(epoch_data)} lines ({len(phoenix_train_items)} Phoenix, {len(all_valid_cnt_lines)} CNT).")
                
                cmd_aug = [
                    sys.executable,
                    "-u",
                    "scripts/augment_dynamic.py",
                    "--manifest", master_manifest_to_use,
                    "--output-dir", master_pool_dir,
                    "--variations-per-image", str(config.variations_per_image),
                    "--error-rate", str(config.error_rate),
                    "--blur-prob", str(config.blur_prob),
                    "--shadow-prob", str(config.shadow_prob),
                    "--distortion-prob", str(config.distortion_prob),
                    "--dropout-prob", str(config.dropout_prob),
                    "--bleedthrough-prob", str(config.bleedthrough_prob),
                    "--distortion-limit", str(config.distortion_limit),
                    "--page-curl-prob", str(config.page_curl_prob),
                    "--page-curl-direction", str(config.page_curl_direction),
                    "--page-curl-bending-factor", str(config.page_curl_bending_factor),
                    "--page-curl-compression-factor", str(config.page_curl_compression_factor),
                    "--page-curl-width-ratio", str(config.page_curl_width_ratio),
                    "--cnt-blur-prob", str(config.cnt_noise["blur"]["prob"]),
                    "--cnt-shadow-prob", str(config.cnt_noise["shadow"]["prob"]),
                    "--cnt-distortion-prob", str(config.cnt_noise["distortion"]["prob"]),
                    "--cnt-dropout-prob", str(config.cnt_noise["dropout"]["prob"]),
                    "--cnt-blur-limit-min", str(config.cnt_noise["blur"]["limit_min"]),
                    "--cnt-blur-limit-max", str(config.cnt_noise["blur"]["limit_max"]),
                    "--cnt-shadow-dimension", str(config.cnt_noise["shadow"]["dimension"]),
                    "--cnt-distortion-limit", str(config.cnt_noise["distortion"]["limit"]),
                    "--cnt-elastic-alpha", str(config.cnt_noise["distortion"].get("elastic_alpha", 1.0)),
                    "--cnt-elastic-sigma", str(config.cnt_noise["distortion"].get("elastic_sigma", 15.0)),
                    "--cnt-use-multi-scale", str(config.cnt_noise["distortion"].get("use_multi_scale", True)),
                    "--cnt-dropout-holes-min", str(config.cnt_noise["dropout"]["holes_min"]),
                    "--cnt-dropout-holes-max", str(config.cnt_noise["dropout"]["holes_max"]),
                    "--cnt-dropout-size-min", str(config.cnt_noise["dropout"]["size_min"]),
                    "--cnt-dropout-size-max", str(config.cnt_noise["dropout"]["size_max"]),
                    "--cnt-micro-dropout-prob", str(config.cnt_noise.get("micro_dropout", {"prob": 0.4})["prob"]),
                    "--cnt-micro-dropout-holes-min", str(config.cnt_noise.get("micro_dropout", {"holes_min": 20})["holes_min"]),
                    "--cnt-micro-dropout-holes-max", str(config.cnt_noise.get("micro_dropout", {"holes_max": 60})["holes_max"]),
                    "--cnt-micro-dropout-size-min", str(config.cnt_noise.get("micro_dropout", {"size_min": 1})["size_min"]),
                    "--cnt-micro-dropout-size-max", str(config.cnt_noise.get("micro_dropout", {"size_max": 2})["size_max"]),
                    "--cnt-smudge-prob", str(config.cnt_noise.get("smudge", {"prob": 0.4})["prob"]),
                    "--cnt-smudge-intensity", str(config.cnt_noise.get("smudge", {"intensity": 0.3})["intensity"]),
                    "--cnt-page-curl-prob", str(config.cnt_noise.get("page_curl", {}).get("prob", 0.0)),
                    "--cnt-page-curl-direction", str(config.cnt_noise.get("page_curl", {}).get("direction", "random")),
                    "--cnt-page-curl-bending-factor", str(config.cnt_noise.get("page_curl", {}).get("bending_factor", 0.15)),
                    "--cnt-page-curl-compression-factor", str(config.cnt_noise.get("page_curl", {}).get("compression_factor", 0.5)),
                    "--cnt-page-curl-width-ratio", str(config.cnt_noise.get("page_curl", {}).get("width_ratio", 0.3)),
                    "--compile-lstmf",
                    "--model-dir", config.model_dir,
                    "--metadata-index", master_index_path
                ]
                print(f"Running augment_dynamic.py to generate master pool...")
                subprocess.run(cmd_aug, check=True)
            else:
                print(f"Master pool already exists at {master_pool_dir}. Reusing compiled master pool.")
            
            current_ratio = config.mixture_ratio
            sched = getattr(config, "mixture_schedule", {})
            if sched.get("enabled", False):
                start_ratio = sched.get("start_ratio", 0.5)
                end_ratio = sched.get("end_ratio", 1.0)
                start_epoch = sched.get("start_epoch", 1)
                end_epoch = sched.get("end_epoch", config.total_epochs)
                
                if epoch <= start_epoch:
                    current_ratio = start_ratio
                elif epoch >= end_epoch:
                    current_ratio = end_ratio
                else:
                    fraction = (epoch - start_epoch) / (end_epoch - start_epoch)
                    current_ratio = start_ratio + fraction * (end_ratio - start_ratio)
                
                print(f"Dynamic Mixture Schedule: Epoch {epoch} target ratio = {current_ratio:.4f}")
            
            from phoenix.training.sweep import SweepSampler
            print(f"Sampling custom training subset with ratio {current_ratio:.4f} for epoch {epoch}...")
            SweepSampler.sample_to_list(
                metadata_index_path=master_index_path,
                output_list_path=list_train_path,
                mixture_ratio=current_ratio,
                epoch=epoch,
                max_cnt_samples=getattr(config, "max_cnt_samples", None)
            )
        else:
            # Original Step B: Generate fresh random dynamic augmentations (only train split)
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
                
                # Calculate required CNT lines based on mixture_ratio or dynamic mixture schedule
                current_ratio = config.mixture_ratio
                sched = getattr(config, "mixture_schedule", {})
                if sched.get("enabled", False):
                    start_ratio = sched.get("start_ratio", 0.5)
                    end_ratio = sched.get("end_ratio", 1.0)
                    start_epoch = sched.get("start_epoch", 1)
                    end_epoch = sched.get("end_epoch", config.total_epochs)
                    
                    if epoch <= start_epoch:
                        current_ratio = start_ratio
                    elif epoch >= end_epoch:
                        current_ratio = end_ratio
                    else:
                        # Linear interpolation
                        fraction = (epoch - start_epoch) / (end_epoch - start_epoch)
                        current_ratio = start_ratio + fraction * (end_ratio - start_ratio)
                    
                    print(f"Dynamic Mixture Schedule: Epoch {epoch} target ratio = {current_ratio:.4f} (Start: {start_ratio:.2f} @ Epoch {start_epoch}, End: {end_ratio:.2f} @ Epoch {end_epoch})")
                
                if current_ratio <= 0.0 or current_ratio > 1.0:
                    raise ValueError(f"Calculated mixture ratio must be in (0, 1], got {current_ratio}")
                
                if current_ratio == 1.0:
                    n_cnt = 0
                else:
                    n_cnt = int(n_phoenix * (1.0 - current_ratio) / current_ratio)
                
                # Cap by max_cnt_samples if specified
                max_cnt_samples = getattr(config, "max_cnt_samples", None)
                if max_cnt_samples is not None:
                    n_cnt = min(n_cnt, max_cnt_samples)
                
                print(f"Computed batch mixture: Phoenix train samples = {n_phoenix}, target CNT samples = {n_cnt} (ratio = {current_ratio:.4f})")
                
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
                print(f"Train set: {train_phoenix_count} Phoenix lines, {train_cnt_count} CNT lines. Actual Phoenix Ratio: {actual_ratio:.4f} (Target: {current_ratio:.4f})")
                
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
                "--page-curl-prob", str(config.page_curl_prob),
                "--page-curl-direction", str(config.page_curl_direction),
                "--page-curl-bending-factor", str(config.page_curl_bending_factor),
                "--page-curl-compression-factor", str(config.page_curl_compression_factor),
                "--page-curl-width-ratio", str(config.page_curl_width_ratio),
                "--cnt-blur-prob", str(config.cnt_noise["blur"]["prob"]),
                "--cnt-shadow-prob", str(config.cnt_noise["shadow"]["prob"]),
                "--cnt-distortion-prob", str(config.cnt_noise["distortion"]["prob"]),
                "--cnt-dropout-prob", str(config.cnt_noise["dropout"]["prob"]),
                "--cnt-blur-limit-min", str(config.cnt_noise["blur"]["limit_min"]),
                "--cnt-blur-limit-max", str(config.cnt_noise["blur"]["limit_max"]),
                "--cnt-shadow-dimension", str(config.cnt_noise["shadow"]["dimension"]),
                "--cnt-distortion-limit", str(config.cnt_noise["distortion"]["limit"]),
                "--cnt-elastic-alpha", str(config.cnt_noise["distortion"].get("elastic_alpha", 1.0)),
                "--cnt-elastic-sigma", str(config.cnt_noise["distortion"].get("elastic_sigma", 15.0)),
                "--cnt-use-multi-scale", str(config.cnt_noise["distortion"].get("use_multi_scale", True)),
                "--cnt-dropout-holes-min", str(config.cnt_noise["dropout"]["holes_min"]),
                "--cnt-dropout-holes-max", str(config.cnt_noise["dropout"]["holes_max"]),
                "--cnt-dropout-size-min", str(config.cnt_noise["dropout"]["size_min"]),
                "--cnt-dropout-size-max", str(config.cnt_noise["dropout"]["size_max"]),
                "--cnt-micro-dropout-prob", str(config.cnt_noise.get("micro_dropout", {"prob": 0.4})["prob"]),
                "--cnt-micro-dropout-holes-min", str(config.cnt_noise.get("micro_dropout", {"holes_min": 20})["holes_min"]),
                "--cnt-micro-dropout-holes-max", str(config.cnt_noise.get("micro_dropout", {"holes_max": 60})["holes_max"]),
                "--cnt-micro-dropout-size-min", str(config.cnt_noise.get("micro_dropout", {"size_min": 1})["size_min"]),
                "--cnt-micro-dropout-size-max", str(config.cnt_noise.get("micro_dropout", {"size_max": 2})["size_max"]),
                "--cnt-smudge-prob", str(config.cnt_noise.get("smudge", {"prob": 0.4})["prob"]),
                "--cnt-smudge-intensity", str(config.cnt_noise.get("smudge", {"intensity": 0.3})["intensity"]),
                "--cnt-page-curl-prob", str(config.cnt_noise.get("page_curl", {}).get("prob", 0.0)),
                "--cnt-page-curl-direction", str(config.cnt_noise.get("page_curl", {}).get("direction", "random")),
                "--cnt-page-curl-bending-factor", str(config.cnt_noise.get("page_curl", {}).get("bending_factor", 0.15)),
                "--cnt-page-curl-compression-factor", str(config.cnt_noise.get("page_curl", {}).get("compression_factor", 0.5)),
                "--cnt-page-curl-width-ratio", str(config.cnt_noise.get("page_curl", {}).get("width_ratio", 0.3))
            ]
            subprocess.run(cmd_aug, check=True)

            # Step C: Compile augmented images to .lstmf files and create list.train
            print("Compiling images to .lstmf files...")
            tiff_files = glob.glob(os.path.join(config.output_dir, "*.tiff"))
            if not tiff_files:
                raise RuntimeError("Error: No augmented TIFFs generated!")

            with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                lstmf_paths = list(executor.map(lambda f: compile_image(f, config.model_dir), tiff_files))

            with open(list_train_path, "w", encoding="utf-8") as list_f:
                for lstmf_path in lstmf_paths:
                    list_f.write(lstmf_path + "\n")

    print("\n=== Staged Epoch Loop finished successfully! ===")
    print(f"Final checkpoints and epoch training logs are in: {config.train_output_dir}")
