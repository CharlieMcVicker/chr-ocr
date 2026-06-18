#!/bin/bash
set -e

echo "Running split_train_test.py to stratify the dataset..."
uv run python scripts/split_train_test.py

echo "Running prepare_splits.sh to generate .lstmf..."
bash scripts/prepare_splits.sh

echo "Running train_staged.py with network expansion (FULL RUN)..."
uv run python scripts/train_staged.py \
  --total-epochs 12 \
  --iterations-per-epoch 200 \
  --learning-rate 0.0005 \
  --train-manifest training_data/manifest_w_lang.json \
  --output-dir training_data/dataset_epoch_full \
  --train-output-dir training_data/dataset_staged_output_full \
  --old-traineddata training_data/dataset/model/chr.traineddata \
  --model-dir training_data/dataset/model/starter/chr \
  --continue-from training_data/dataset/model/chr.lstm

echo "Full training run complete. Check training_data/dataset_staged_output for results."
