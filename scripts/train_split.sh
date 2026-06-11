#!/bin/bash
set -e

ITERATIONS=${1:-200}
RUN_ID=$(date +%Y%m%d_%H%M%S)

DATASET_DIR="training_data_v2/dataset"
TRAIN_DIR="${DATASET_DIR}/train_80"
MODEL_DIR="${DATASET_DIR}/model"
OUTPUT_DIR="${DATASET_DIR}/output_split_${RUN_ID}"

mkdir -p "$OUTPUT_DIR"

echo "Starting lstmtraining on 80% split (${ITERATIONS} iterations)..."
echo "  Output dir : $OUTPUT_DIR"
echo "  Log file   : $OUTPUT_DIR/training.log"

lstmtraining \
  --continue_from "$MODEL_DIR/chr.lstm" \
  --model_output "$OUTPUT_DIR/chr" \
  --traineddata "$MODEL_DIR/chr.traineddata" \
  --train_listfile "$TRAIN_DIR/list.train" \
  --max_iterations "$ITERATIONS" > "$OUTPUT_DIR/training.log" 2>&1

echo "Training complete! Log: $OUTPUT_DIR/training.log"
echo "Checkpoints in: $OUTPUT_DIR"
