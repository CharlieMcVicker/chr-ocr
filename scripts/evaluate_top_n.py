import argparse
import os
import subprocess
import shutil
import tempfile


def compile_model(checkpoint_path):
    """
    compile the model into a temp file to do eval with
    """
    # make a sibling file with the suffix .compiled
    temp_model_path = checkpoint_path + ".compiled"
    subprocess.run(
        [
            "lstmtraining",
            "--stop_training",
            "--continue_from",
            checkpoint_path,
            "--traineddata",
            "dataset/model/chr.traineddata",
            "--model_output",
            temp_model_path,
        ]
    )
    return temp_model_path


def run_eval(model_path):
    temp_model_path = compile_model(model_path)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Tesseract expects a directory containing {lang}.traineddata
        traineddata_path = os.path.join(tmpdir, "chr.traineddata")
        shutil.move(temp_model_path, traineddata_path)
        
        print("Running eval on model: " + model_path)
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "scripts/evaluate_mixed_model.py",
                "--model-dir",
                tmpdir,
            ]
        )


if __name__ == "__main__":
    # Get args from dir for the folder w model checkpoints
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, required=True)
    args = parser.parse_args()

    checkpoints = [
        os.path.join(args.model_dir, f)
        for f in os.listdir(args.model_dir)
        if f.endswith(".checkpoint")
    ]

    iteration_num = lambda s: int(s.split("_")[-1].split(".")[0])

    checkpoints_sorted = sorted(checkpoints, key=iteration_num)

    top_n = 5

    for checkpoint in checkpoints_sorted[-top_n:]:
        run_eval(checkpoint)
