#!/bin/bash
set -e

# Find the latest output directory
OUTPUT_DIR=$(ls -td training_data_v2/dataset/output_split_* | head -n 1)
CHECKPOINT=$(ls -t "$OUTPUT_DIR"/chr*.checkpoint | head -n 1)

if [ -z "$CHECKPOINT" ]; then
    echo "No checkpoint found in $OUTPUT_DIR"
    exit 1
fi

echo "Evaluating checkpoint: $CHECKPOINT"
lstmeval \
  --model "$CHECKPOINT" \
  --traineddata training_data_v2/dataset/model/chr.traineddata \
  --eval_listfile training_data_v2/dataset/test_20/list.test \
  2>&1 | tee "$OUTPUT_DIR/eval_results.txt"
