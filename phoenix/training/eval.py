"""
Modular checkpoint evaluation, slicing, and best-performing model tracking.
"""
import os
import re
import glob
import json
import shutil
import subprocess
import sys

def get_iteration_num(cp_path):
    try:
        basename = os.path.basename(cp_path)
        part = basename.split("_")[-1].split(".")[0]
        if part.isdigit():
            return int(part)
    except Exception:
        pass
    match = re.findall(r"\d+", cp_path)
    if match:
        return int(match[-1])
    return 0

def get_sorted_checkpoints(train_output_dir: str, slice_str: str = "[-5:]") -> list[str]:
    """
    Finds and sorts all checkpoints in the train_output_dir by iteration number,
    and applies the specified Python slice string (e.g. '[-10:-5]').
    """
    checkpoints = glob.glob(os.path.join(train_output_dir, "*.checkpoint"))
    if not checkpoints:
        return []
    
    checkpoints_sorted = sorted(checkpoints, key=get_iteration_num)
    
    # Safely apply the slice_str using eval with restricted environment
    if slice_str:
        try:
            # Strip outer brackets if provided e.g. [-10:-5] -> -10:-5
            s = slice_str.strip()
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1]
            
            parts = s.split(":")
            if len(parts) == 1:
                idx = int(parts[0])
                return [checkpoints_sorted[idx]]
            elif len(parts) == 2:
                start = int(parts[0]) if parts[0] else None
                end = int(parts[1]) if parts[1] else None
                return checkpoints_sorted[slice(start, end)]
            elif len(parts) == 3:
                start = int(parts[0]) if parts[0] else None
                end = int(parts[1]) if parts[1] else None
                step = int(parts[2]) if parts[2] else None
                return checkpoints_sorted[slice(start, end, step)]
        except Exception as e:
            print(f"Warning: Failed to parse slice string '{slice_str}': {e}. Defaulting to all checkpoints.")
            
    return checkpoints_sorted

def compile_checkpoint(checkpoint_path: str, traineddata_path: str, output_path: str) -> bool:
    """
    Compiles a .checkpoint into a .traineddata model using lstmtraining --stop_training.
    """
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except Exception:
            pass

    unpack_cmd = [
        "lstmtraining",
        "--stop_training",
        "--continue_from", checkpoint_path,
        "--traineddata", traineddata_path,
        "--model_output", output_path
    ]
    try:
        subprocess.run(unpack_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"Failed to compile checkpoint {checkpoint_path} to {output_path}: {e}")
        return False

def evaluate_checkpoint(checkpoint_path: str, traineddata_path: str, train_output_dir: str, lang: str, skip_cnt: bool = False) -> dict:
    """
    Evaluates a compiled .traineddata model on the test splits and parses its performance metrics.
    """
    # Run evaluate_mixed_model.py
    eval_cmd = [
        sys.executable,
        "scripts/evaluate_mixed_model.py",
        "--model-dir", train_output_dir,
        "--lang", lang
    ]
    if skip_cnt:
        eval_cmd.append("--skip-cnt")
    try:
        res = subprocess.run(eval_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        eval_stdout = res.stdout
    except Exception as e:
        print(f"Failed to run evaluate_mixed_model.py: {e}")
        return {}

    # Parse metrics
    phx_cer, phx_wer = None, None
    cnt_cer, cnt_wer = None, None
    weighted_cer, weighted_wer = None, None

    phx_match = re.search(r"Phoenix Test Set \(\d+ lines\):\s+Mean CER:\s+([\d\.]+)%\s+Mean WER:\s+([\d\.]+)%", eval_stdout)
    if phx_match:
        phx_cer = float(phx_match.group(1))
        phx_wer = float(phx_match.group(2))
        
    cnt_match = re.search(r"CNT Test Set \(\d+ lines\):\s+Mean CER:\s+([\d\.]+)%\s+Mean WER:\s+([\d\.]+)%", eval_stdout)
    if cnt_match:
        cnt_cer = float(cnt_match.group(1))
        cnt_wer = float(cnt_match.group(2))
        
    weighted_match = re.search(r"Overall Combined Weighted Performance \(\d+ lines total\):\s+Weighted Mean CER:\s+([\d\.]+)%\s+Weighted Mean WER:\s+([\d\.]+)%", eval_stdout)
    if weighted_match:
        weighted_cer = float(weighted_match.group(1))
        weighted_wer = float(weighted_match.group(2))

    if weighted_cer is None:
        print(f"Could not parse metrics from evaluation output of {checkpoint_path}.")
        return {}

    return {
        "phoenix_CER": phx_cer,
        "phoenix_WER": phx_wer,
        "cnt_CER": cnt_cer,
        "cnt_WER": cnt_wer,
        "weighted_CER": weighted_cer,
        "weighted_WER": weighted_wer,
        "checkpoint_path": checkpoint_path
    }

def track_and_update_bests(checkpoint_path: str, metrics: dict, config_path: str, best_dir: str = "best_model", temp_traineddata: str = None):
    """
    Checks if the given checkpoint sets a new historical record for either
    Phoenix CER or Weighted CER. If so, updates the corresponding folder.
    """
    os.makedirs(best_dir, exist_ok=True)
    
    subdirs = {
        "phoenix": {
            "path": os.path.join(best_dir, "phoenix"),
            "metric_key": "phoenix_CER",
            "display_name": "Phoenix CER"
        },
        "weighted": {
            "path": os.path.join(best_dir, "weighted"),
            "metric_key": "weighted_CER",
            "display_name": "Overall Combined Weighted CER"
        }
    }
    
    for key, settings in subdirs.items():
        subdir_path = settings["path"]
        metric_key = settings["metric_key"]
        display_name = settings["display_name"]
        
        os.makedirs(subdir_path, exist_ok=True)
        stats_path = os.path.join(subdir_path, "scoring_stats.json")
        
        current_val = metrics.get(metric_key)
        if current_val is None:
            continue
            
        should_update = False
        if not os.path.exists(stats_path):
            print(f"No previous best found for {display_name}. Saving current checkpoint as the best {key} model.")
            should_update = True
        else:
            try:
                with open(stats_path, "r", encoding="utf-8") as f:
                    prev_stats = json.load(f)
                prev_val = prev_stats.get(metric_key)
                if prev_val is None or current_val < prev_val:
                    print(f"New global best {display_name} model found! Improved from {prev_val}% to {current_val}%.")
                    should_update = True
                else:
                    print(f"Current checkpoint ({display_name}: {current_val}%) did not beat global best ({display_name}: {prev_val}%).")
            except Exception as e:
                print(f"Error reading previous stats for {display_name}, overwriting: {e}")
                should_update = True
                
        if should_update:
            # Copy checkpoint
            shutil.copy2(checkpoint_path, os.path.join(subdir_path, "best.checkpoint"))
            # Copy config
            shutil.copy2(config_path, os.path.join(subdir_path, "best_config.json"))
            # Copy compiled traineddata if provided
            if temp_traineddata and os.path.exists(temp_traineddata):
                shutil.copy2(temp_traineddata, os.path.join(subdir_path, "best.traineddata"))
                
            # Write stats
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            print(f"Updated best {key} model files in {subdir_path}/")
            
            # If we updated Phoenix, also mirror it to the root of best_dir
            if key == "phoenix":
                print(f"Mirroring best Phoenix CER model to root of {best_dir}/")
                shutil.copy2(checkpoint_path, os.path.join(best_dir, "best.checkpoint"))
                shutil.copy2(config_path, os.path.join(best_dir, "best_config.json"))
                if temp_traineddata and os.path.exists(temp_traineddata):
                    shutil.copy2(temp_traineddata, os.path.join(best_dir, "best.traineddata"))
                with open(os.path.join(best_dir, "scoring_stats.json"), "w", encoding="utf-8") as f:
                    json.dump(metrics, f, indent=2, ensure_ascii=False)
