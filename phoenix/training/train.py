"""
Staged Epoch Loop supervisor script for dynamic augmentation generation and Tesseract model training.
Orchestrates Tesseract training epoch-by-epoch while maintaining a low disk footprint.
"""

import os
import sys
import math
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
            pool_name = f"{config.master_pool_prefix}_epoch_{epoch}" if config.master_pool_prefix else f"master_pool_epoch_{epoch}"
            master_pool_dir = f"training_data/staged_tuning/{pool_name}"
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
                
                # Dynamically calculate maximum CNT samples needed in the master pool
                n_phoenix = len(phoenix_train_items)
                min_ratio = config.mixture_ratio
                sched = getattr(config, "mixture_schedule", {})
                if sched.get("enabled", False):
                    min_ratio = min(min_ratio, sched.get("start_ratio", 0.5), sched.get("end_ratio", 1.0))
                
                if min_ratio < 0.0 or min_ratio > 1.0:
                    raise ValueError(f"Mixture ratio must be in [0, 1], got {min_ratio}")
                
                if min_ratio == 0.0:
                    pretrain_cap = getattr(config, "pretrain_cnt_cap", None)
                    if pretrain_cap is not None:
                        max_needed_cnt = pretrain_cap
                    else:
                        max_needed_cnt = 32231
                else:
                    if min_ratio <= 0.05:
                        min_ratio = 0.05
                    max_needed_cnt = int(n_phoenix * (1.0 - min_ratio) / min_ratio)
                
                max_cnt_samples = getattr(config, "max_cnt_samples", None)
                if max_cnt_samples is not None:
                    max_needed_cnt = min(max_needed_cnt, max_cnt_samples)
                
                # Add 20% safety margin and clamp to [500, 2000] if not pure pretraining
                if min_ratio > 0.0:
                    max_needed_cnt = int(max_needed_cnt * 1.2)
                    max_needed_cnt = max(500, min(max_needed_cnt, 2000))
                
                # Load rare characters list for priority sampling
                rare_chars = set()
                rare_chars_path = "training_data/rare_characters.json"
                if os.path.exists(rare_chars_path):
                    try:
                        with open(rare_chars_path, "r", encoding="utf-8") as f:
                            rare_chars = set(json.load(f))
                    except Exception:
                        pass

                import random
                seed_str = f"cnt_master_pool_salt_epoch_{epoch}"
                rng = random.Random(seed_str)
                
                rare_cnt_lines = []
                common_cnt_lines = []
                for x in all_valid_cnt_lines:
                    text = x["line"].get("ftm_aligned", "")
                    if any(c in text for c in rare_chars):
                        rare_cnt_lines.append(x)
                    else:
                        common_cnt_lines.append(x)
                
                rng.shuffle(rare_cnt_lines)
                rng.shuffle(common_cnt_lines)
                
                sampled_count = min(max_needed_cnt, len(all_valid_cnt_lines))
                if len(rare_cnt_lines) >= sampled_count:
                    all_valid_cnt_lines = rare_cnt_lines[:sampled_count]
                else:
                    needed = sampled_count - len(rare_cnt_lines)
                    all_valid_cnt_lines = rare_cnt_lines + common_cnt_lines[:needed]
                
                print(f"Master Pool: Calculated max needed CNT lines is {max_needed_cnt} (min_ratio={min_ratio:.4f}, n_phoenix={n_phoenix}).")
                print(f"Master Pool: Reduced CNT lines from 32,231 to {len(all_valid_cnt_lines)} (prioritizing rare characters) to accelerate pool generation.")
                
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
                if config.use_cached_cnt:
                    manifest_for_augmentation = {k: v for k, v in epoch_data.items() if v.get("dataset") != "cnt"}
                else:
                    manifest_for_augmentation = epoch_data

                with open(master_manifest_to_use, "w", encoding="utf-8") as f:
                    json.dump(manifest_for_augmentation, f, ensure_ascii=False, indent=2)
                
                print(f"Generated master manifest with {len(epoch_data)} lines ({len(phoenix_train_items)} Phoenix, {len(all_valid_cnt_lines)} CNT).")
                
                cmd_aug = [
                    sys.executable,
                    "-u",
                    "scripts/augment_dynamic.py",
                    "--manifest", master_manifest_to_use,
                    "--output-dir", master_pool_dir,
                    "--variations-per-image", str(getattr(config, "master_pool_variations", None) or config.variations_per_image),
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
                    "--cnt-micro-dropout-prob", str(config.cnt_noise.get("micro_dropout", {}).get("prob", 0.4)),
                    "--cnt-micro-dropout-holes-min", str(config.cnt_noise.get("micro_dropout", {}).get("holes_min", 20)),
                    "--cnt-micro-dropout-holes-max", str(config.cnt_noise.get("micro_dropout", {}).get("holes_max", 60)),
                    "--cnt-micro-dropout-size-min", str(config.cnt_noise.get("micro_dropout", {}).get("size_min", 1)),
                    "--cnt-micro-dropout-size-max", str(config.cnt_noise.get("micro_dropout", {}).get("size_max", 2)),
                    "--cnt-smudge-prob", str(config.cnt_noise.get("smudge", {}).get("prob", 0.4)),
                    "--cnt-smudge-intensity", str(config.cnt_noise.get("smudge", {}).get("intensity", 0.3)),

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

                if config.use_cached_cnt:
                    cache_manifest_path = os.path.join(config.cnt_cache_dir, "cnt_cache_manifest.json")
                    if not os.path.exists(cache_manifest_path):
                        raise FileNotFoundError(f"CNT cache manifest not found at {cache_manifest_path}. Please run scripts/pre_augment_cnt.py first.")
                    with open(cache_manifest_path, "r", encoding="utf-8") as f:
                        cnt_cache = json.load(f)
                    
                    with open(master_index_path, "r", encoding="utf-8") as f:
                        metadata_records = json.load(f)
                    
                    print("Loading pre-augmented and cached CNT records into master pool...")
                    cached_cnt_added = 0
                    for item_info in all_valid_cnt_lines:
                        item_id = f"cnt_{item_info['book_idx']:02d}_{item_info['verse_key']}_line_{item_info['line_idx']:02d}"
                        if item_id in cnt_cache:
                            for var_rec in cnt_cache[item_id]:
                                lstmf = var_rec.get("lstmf_path")
                                if not lstmf or not os.path.exists(lstmf):
                                    tiff_path = var_rec.get("tiff_path")
                                    if tiff_path and os.path.exists(tiff_path):
                                        try:
                                            lstmf = compile_image(tiff_path, config.model_dir)
                                            var_rec["lstmf_path"] = lstmf
                                        except Exception as e:
                                            print(f"Error compiling cached tiff {tiff_path}: {e}")
                                metadata_records.append(var_rec)
                                cached_cnt_added += 1
                        else:
                            print(f"Warning: Cached records for {item_id} not found in cache manifest!")
                    
                    with open(master_index_path, "w", encoding="utf-8") as f:
                        json.dump(metadata_records, f, indent=2, ensure_ascii=False)
                    print(f"Added {cached_cnt_added} cached CNT variation records to master pool index.")
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
                max_cnt_samples=getattr(config, "max_cnt_samples", None),
                target_vars=getattr(config, "variations_per_image", None)
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
                
                if current_ratio < 0.0 or current_ratio > 1.0:
                    raise ValueError(f"Calculated mixture ratio must be in [0, 1], got {current_ratio}")
                
                if current_ratio == 1.0:
                    n_cnt = 0
                elif current_ratio == 0.0:
                    pretrain_cap = getattr(config, "pretrain_cnt_cap", None)
                    if pretrain_cap is not None:
                        n_cnt = pretrain_cap
                    else:
                        n_cnt = 9999999
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
                        if current_ratio == 0.0 and v.get("dataset") != "cnt":
                            continue
                        epoch_data[k] = v
                    elif v.get("split") == "test":
                        # Keep test items in manifest if they are needed for reference, but train listfile will only compile train items
                        epoch_data[k] = v
                
                manifest_to_use = os.path.join(config.output_dir, f"manifest_epoch_{epoch}.json")
                if config.use_cached_cnt:
                    manifest_for_augmentation = {k: v for k, v in epoch_data.items() if v.get("dataset") != "cnt"}
                else:
                    manifest_for_augmentation = epoch_data

                with open(manifest_to_use, "w", encoding="utf-8") as f:
                    json.dump(manifest_for_augmentation, f, ensure_ascii=False, indent=2)
                
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
            if not tiff_files and not config.use_cached_cnt:
                raise RuntimeError("Error: No augmented TIFFs generated!")

            with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
                lstmf_paths = list(executor.map(lambda f: compile_image(f, config.model_dir), tiff_files))

            if config.use_cached_cnt:
                cache_manifest_path = os.path.join(config.cnt_cache_dir, "cnt_cache_manifest.json")
                if not os.path.exists(cache_manifest_path):
                    raise FileNotFoundError(f"CNT cache manifest not found at {cache_manifest_path}. Please run scripts/pre_augment_cnt.py first.")
                with open(cache_manifest_path, "r", encoding="utf-8") as f:
                    cnt_cache = json.load(f)
                    
                # Append cached CNT lstmf paths
                cached_cnt_lstmf_paths = []
                for item_info in sampled_lines:
                    item_id = f"cnt_{item_info['book_idx']:02d}_{item_info['verse_key']}_line_{item_info['line_idx']:02d}"
                    if item_id in cnt_cache:
                        for var_rec in cnt_cache[item_id]:
                            lstmf = var_rec.get("lstmf_path")
                            if lstmf and os.path.exists(lstmf):
                                cached_cnt_lstmf_paths.append(lstmf)
                            else:
                                # If lstmf is not pre-compiled or not found, compile it now from the cached tiff
                                tiff_path = var_rec.get("tiff_path")
                                if tiff_path and os.path.exists(tiff_path):
                                    print(f"Compiling cached tiff {tiff_path} to lstmf...")
                                    try:
                                        compiled = compile_image(tiff_path, config.model_dir)
                                        cached_cnt_lstmf_paths.append(compiled)
                                        var_rec["lstmf_path"] = compiled
                                    except Exception as e:
                                        print(f"Error compiling cached tiff {tiff_path}: {e}")
                    else:
                        print(f"Warning: Cached records for {item_id} not found in cache manifest!")
                        
                print(f"Adding {len(cached_cnt_lstmf_paths)} cached CNT lstmf files to training list.")
                lstmf_paths.extend(cached_cnt_lstmf_paths)

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
        elif config.lr_schedule == "cosine_warmup":
            warmup_epochs = config.lr_warmup_epochs
            if epoch <= warmup_epochs:
                if warmup_epochs > 0:
                    current_lr = config.learning_rate * (epoch / warmup_epochs)
                else:
                    current_lr = config.learning_rate
            else:
                t_max = config.lr_t_max if config.lr_t_max is not None else (config.total_epochs - warmup_epochs)
                t = epoch - warmup_epochs
                eta_min = config.lr_eta_min
                if t_max > 0:
                    t = min(t, t_max)
                    current_lr = eta_min + 0.5 * (config.learning_rate - eta_min) * (1 + math.cos(math.pi * t / t_max))
                else:
                    current_lr = eta_min
            
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

        # Parse and log training metrics from the log file
        try:
            import re
            import csv
            import time
            
            metrics_path = os.path.join(config.train_output_dir, "metrics.csv")
            file_exists = os.path.exists(metrics_path)
            
            parsed_rows = []
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("At iteration "):
                            try:
                                iter_match = re.search(r"At iteration (\d+)", line)
                                if not iter_match:
                                    continue
                                iteration = int(iter_match.group(1))
                                
                                def get_float(pattern, text):
                                    m = re.search(pattern, text)
                                    return float(m.group(1)) if m else 0.0
 
                                mean_rms = get_float(r"mean rms=([\d.-]+)%", line)
                                delta = get_float(r"delta=([\d.-]+)%", line)
                                bcer_train = get_float(r"BCER train=([\d.-]+)%", line)
                                bwer_train = get_float(r"BWER train=([\d.-]+)%", line)
                                skip_ratio = get_float(r"skip ratio=([\d.-]+)%", line)
                                
                                parsed_rows.append([
                                    iteration,
                                    time.time(),
                                    mean_rms,
                                    delta,
                                    bcer_train,
                                    bwer_train,
                                    skip_ratio,
                                    "", "", "", "", "", ""
                                ])
                            except Exception as parse_err:
                                print(f"Error parsing training log line: {parse_err}", file=sys.stderr)
            
            if parsed_rows:
                with open(metrics_path, "a", newline="", encoding="utf-8") as csv_f:
                    writer = csv.writer(csv_f)
                    if not file_exists:
                        writer.writerow([
                            "iteration",
                            "wall_time",
                            "train_loss",
                            "delta",
                            "bcer_train",
                            "bwer_train",
                            "skip_ratio",
                            "phoenix_cer",
                            "phoenix_wer",
                            "cnt_cer",
                            "cnt_wer",
                            "weighted_cer",
                            "weighted_wer"
                        ])
                    writer.writerows(parsed_rows)
                print(f"Logged {len(parsed_rows)} iteration metrics to {metrics_path}")
        except Exception as csv_err:
            print(f"Error logging training metrics to CSV: {csv_err}", file=sys.stderr)

        # Step F: Clean up temporary epoch augmented images and .lstmf files to preserve disk space
        print(f"Cleaning up temporary epoch files in {config.output_dir}...")
        # Save manifest_epoch_{epoch}.json to train_output_dir for verification
        if config.use_dynamic_cnt:
            if 'manifest_to_use' in locals() and manifest_to_use and os.path.exists(manifest_to_use):
                shutil.copy2(manifest_to_use, os.path.join(config.train_output_dir, f"manifest_epoch_{epoch}.json"))
            elif config.use_shared_pool:
                pool_name = f"{config.master_pool_prefix}_epoch_{epoch}" if config.master_pool_prefix else f"master_pool_epoch_{epoch}"
                master_manifest = os.path.join(f"training_data/staged_tuning/{pool_name}", f"master_manifest_epoch_{epoch}.json")
                if os.path.exists(master_manifest):
                    shutil.copy2(master_manifest, os.path.join(config.train_output_dir, f"manifest_epoch_{epoch}.json"))
        
        if os.path.exists(config.output_dir):
            shutil.rmtree(config.output_dir)

    print("\n=== Staged Epoch Loop finished successfully! ===")
    print(f"Final checkpoints and epoch training logs are in: {config.train_output_dir}")
