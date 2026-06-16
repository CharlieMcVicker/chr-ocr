#!/bin/bash
set -e

DATASET_DIR="training_data/dataset"
TEST_DIR="${DATASET_DIR}/test"
MODEL_DIR=${1:-"${DATASET_DIR}/output"}

# Find the best checkpoint model
CHECKPOINT=$(ls -t "$MODEL_DIR"/*.checkpoint | head -n 1)

echo "Using model: $CHECKPOINT"

echo "" > eval_results.txt

for algo_dir in "$TEST_DIR"/*; do
    if [ -d "$algo_dir" ]; then
        algo=$(basename "$algo_dir")
        echo "Evaluating algo: $algo"
        rm -f "$algo_dir/list.test"
        
        # Generate lstmf for test images
        for img in "$algo_dir"/*.png; do
            base="${img%.png}"
            if [ ! -f "${base}.lstmf" ]; then
                tesseract "$img" "$base" -l chr --psm 13 lstm.train > /dev/null 2>&1
            fi
            echo "$(realpath "${base}.lstmf")" >> "$algo_dir/list.test"
        done
        
        echo "Running lstmeval for $algo..."
        lstmeval \
          --model "$CHECKPOINT" \
          --traineddata "training_data/dataset/model/chr.traineddata" \
          --eval_listfile "$algo_dir/list.test" \
          2>&1 | tee -a eval_results.txt
          
        echo "--------------------------"
    fi
done

echo "Done evaluating!"
