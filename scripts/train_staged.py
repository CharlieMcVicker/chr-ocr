#!/usr/bin/env python3
"""
Staged Epoch Loop supervisor script for dynamic augmentation generation and Tesseract model training.
Orchestrates Tesseract training epoch-by-epoch while maintaining a low disk footprint.
"""
import os
import sys
import glob
import subprocess
import argparse
import shutil
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from config import TrainingConfig

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
    subprocess.run(
        ["tesseract", img_path, base, "--tessdata-dir", model_dir, "-l", "chr", "--oem", "1", "--psm", "13", "/opt/homebrew/share/tessdata/configs/lstm.train"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    return os.path.abspath(base + ".lstmf")

def main():
    parser = argparse.ArgumentParser(description="Staged Epoch Loop for Tesseract OCR Fine-tuning")
    parser.add_argument("--config", default=None, help="Path to JSON configuration file (overrides other command line options)")
    parser.add_argument("--total-epochs", type=int, default=12, help="Total number of staged training epochs")
    parser.add_argument("--iterations-per-epoch", type=int, default=200, help="Number of training iterations to run per epoch")
    parser.add_argument("--train-manifest", default="training_data/manifest_w_lang.json", help="Path to raw master manifest")
    parser.add_argument("--variations-per-image", type=int, default=3, help="Fresh variations to generate per source image each epoch")
    parser.add_argument("--error-rate", type=float, default=0.05, help="Weakly supervised synthetic transcription error rate")
    parser.add_argument("--output-dir", default="training_data/dataset_epoch", help="Temporary directory for epoch dynamic dataset")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Directory containing base models")
    parser.add_argument("--train-output-dir", default="training_data/dataset_staged_output", help="Directory where checkpoints and logs are saved")
    parser.add_argument("--continue-from", default=None, help="Explicit checkpoint path to start training from")
    parser.add_argument("--old-traineddata", default=None, help="Path to the original traineddata (required for network expansion)")
    parser.add_argument("--max-workers", type=int, default=None, help="Maximum number of worker threads for parallel compilation")
    parser.add_argument("--learning-rate", type=float, default=0.0005, help="Learning rate for lstmtraining")
    parser.add_argument("--lr-schedule", default="constant", choices=["constant", "step", "exp"], help="Learning rate schedule type")
    parser.add_argument("--lr-decay-rate", type=float, default=0.5, help="Decay factor for learning rate schedule")
    parser.add_argument("--lr-decay-epochs", type=int, default=4, help="Epoch interval for step decay")
    parser.add_argument("--blur-prob", type=float, default=0.4, help="Probability of blur augmentation")
    parser.add_argument("--shadow-prob", type=float, default=0.3, help="Probability of shadow augmentation")
    parser.add_argument("--distortion-prob", type=float, default=0.4, help="Probability of distortion augmentation")
    parser.add_argument("--dropout-prob", type=float, default=0.3, help="Probability of dropout augmentation")
    parser.add_argument("--bleedthrough-prob", type=float, default=0.25, help="Probability of bleedthrough augmentation")
    args = parser.parse_args()

    # Load configuration
    if args.config:
        print(f"Loading configuration from JSON: {args.config}")
        config = TrainingConfig.load_from_json(args.config)
    else:
        # Build config from command line arguments
        config_data = vars(args)
        # remove config field itself
        config_data.pop("config", None)
        config = TrainingConfig.from_dict(config_data)

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
        print("Generating fresh dynamic augmentations...")
        cmd_aug = [
            ".venv/bin/python",
            "scripts/augment_dynamic.py",
            "--manifest", config.train_manifest,
            "--output-dir", config.output_dir,
            "--variations-per-image", str(config.variations_per_image),
            "--error-rate", str(config.error_rate),
            "--blur-prob", str(config.blur_prob),
            "--shadow-prob", str(config.shadow_prob),
            "--distortion-prob", str(config.distortion_prob),
            "--dropout-prob", str(config.dropout_prob),
            "--bleedthrough-prob", str(config.bleedthrough_prob)
        ]
        subprocess.run(cmd_aug, check=True)

        # Step C: Compile augmented images to .lstmf files and create list.train
        print("Compiling images to .lstmf files...")
        png_files = glob.glob(os.path.join(config.output_dir, "*.png"))
        if not png_files:
            print("Error: No augmented PNGs generated!", file=sys.stderr)
            sys.exit(1)

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
        shutil.rmtree(config.output_dir)

    print("\n=== Staged Epoch Loop finished successfully! ===")
    print(f"Final checkpoints and epoch training logs are in: {config.train_output_dir}")

if __name__ == "__main__":
    main()
