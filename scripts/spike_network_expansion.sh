#!/bin/bash
set -e

echo "Running split_train_test.py to stratify the dataset..."
uv run python scripts/split_train_test.py

echo "Running prepare_splits.sh to generate .lstmf..."
bash scripts/prepare_splits.sh

echo "Running train_staged.py with network expansion (SPIKE)..."
uv run python scripts/train_staged.py \
  --total-epochs 2 \
  --iterations-per-epoch 50 \
  --train-manifest training_data/manifest_w_lang.json \
  --output-dir training_data/dataset_epoch_spike \
  --train-output-dir training_data/dataset_staged_output_spike \
  --old-traineddata training_data/dataset/model/chr.traineddata \
  --model-dir training_data/dataset/model/starter/chr \
  --continue-from training_data/dataset/model/chr.lstm

echo "Spike complete. Check training_data/dataset_staged_output_spike for results."
