#!/bin/bash
set -e

DATASET_DIR="training_data_v2/dataset"
TEST_DIR="${DATASET_DIR}/test"
MODEL_DIR="${DATASET_DIR}/output"

# Find the best checkpoint model
CHECKPOINT=$(ls -t "$MODEL_DIR"/*.checkpoint | head -n 1)

echo "Using model: $CHECKPOINT"

ALGOS=("base" "otsu" "su" "sauvola" "wolf")

echo "" > eval_results.txt

for algo in "${ALGOS[@]}"; do
    ALGO_DIR="$TEST_DIR/$algo"
    
    echo "Evaluating algo: $algo"
    rm -f "$ALGO_DIR/list.test"
    
    # Generate lstmf for test images
    for img in "$ALGO_DIR"/*.png; do
        base="${img%.png}"
        if [ ! -f "${base}.lstmf" ]; then
            tesseract "$img" "$base" -l chr --psm 13 lstm.train > /dev/null 2>&1
        fi
        echo "$(realpath "${base}.lstmf")" >> "$ALGO_DIR/list.test"
    done
    
    echo "Running lstmeval for $algo..."
    lstmeval \
      --model "$CHECKPOINT" \
      --traineddata "training_data_v2/dataset/model/chr.traineddata" \
      --eval_listfile "$ALGO_DIR/list.test" \
      2>&1 | tee -a eval_results.txt
      
    echo "--------------------------"
done

echo "Done evaluating!"
cat eval_results.txt
