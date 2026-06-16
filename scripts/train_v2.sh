#!/bin/bash
set -e

ITERATIONS=${1:-100}
RUN_ID=$(date +%Y%m%d_%H%M%S)

DATASET_DIR="training_data/dataset"
TRAIN_DIR="${DATASET_DIR}/train"
MODEL_DIR="${DATASET_DIR}/model"
OUTPUT_DIR="${DATASET_DIR}/output_${ITERATIONS}_${RUN_ID}"

mkdir -p "$MODEL_DIR"
mkdir -p "$OUTPUT_DIR"

echo "Generating .lstmf files from .png in $TRAIN_DIR..."
rm -f "$TRAIN_DIR/list.train"

for img in "$TRAIN_DIR"/*.png; do
    base="${img%.png}"
    if [ ! -f "${base}.lstmf" ]; then
        tesseract "$img" "$base" -l chr --psm 13 lstm.train > /dev/null 2>&1
    fi
    # Use realpath so lstmtraining can find them from anywhere
    echo "$(realpath "${base}.lstmf")" >> "$TRAIN_DIR/list.train"
done

echo "Generated $(wc -l < "$TRAIN_DIR/list.train" | xargs) entries in list.train"

# 1. Download base model if not exists
cd "$MODEL_DIR"
if [ ! -f "chr.traineddata" ]; then
    echo "Downloading chr.traineddata from tessdata_best..."
    curl -s -L -o chr.traineddata "https://github.com/tesseract-ocr/tessdata_best/raw/main/chr.traineddata"
fi

# 2. Extract LSTM model from traineddata
if [ ! -f "chr.lstm" ]; then
    echo "Extracting chr.lstm from chr.traineddata..."
    combine_tessdata -u chr.traineddata chr.
fi
cd - > /dev/null

# 3. Run lstmtraining
echo "Starting lstmtraining run (${ITERATIONS} iterations)..."
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
