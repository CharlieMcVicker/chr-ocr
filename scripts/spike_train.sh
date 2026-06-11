#!/bin/bash
set -e

# Setup directories
mkdir -p dataset/model
mkdir -p output

cd dataset/model

# 1. Download base model if not exists
if [ ! -f "chr.traineddata" ]; then
    echo "Downloading chr.traineddata from tessdata_best..."
    curl -L -o chr.traineddata "https://github.com/tesseract-ocr/tessdata_best/raw/main/chr.traineddata"
fi

# 2. Extract LSTM model from traineddata
if [ ! -f "chr.lstm" ]; then
    echo "Extracting chr.lstm from chr.traineddata..."
    combine_tessdata -u chr.traineddata chr.
fi

cd ../..

# 3. Run lstmtraining
echo "Starting lstmtraining spike (100 iterations)..."
lstmtraining \
  --continue_from dataset/model/chr.lstm \
  --model_output output/chr \
  --traineddata dataset/model/chr.traineddata \
  --train_listfile dataset/train/list.train \
  --max_iterations 100

echo "Training spike complete! Check the 'output' directory for checkpoints."
