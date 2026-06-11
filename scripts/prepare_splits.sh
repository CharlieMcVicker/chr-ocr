#!/bin/bash
set -e

DATASET_DIR="training_data_v2/dataset"
TRAIN_80_DIR="${DATASET_DIR}/train_80"
TEST_20_DIR="${DATASET_DIR}/test_20"

echo "Generating .lstmf files for TRAIN_80..."
rm -f "$TRAIN_80_DIR/list.train"
for img in "$TRAIN_80_DIR"/*.png; do
    base="${img%.png}"
    if [ ! -f "${base}.lstmf" ]; then
        tesseract "$img" "$base" -l chr --psm 13 lstm.train > /dev/null 2>&1
    fi
    echo "$(realpath "${base}.lstmf")" >> "$TRAIN_80_DIR/list.train"
done
echo "Generated $(wc -l < "$TRAIN_80_DIR/list.train" | xargs) entries in $TRAIN_80_DIR/list.train"

echo "Generating .lstmf files for TEST_20..."
rm -f "$TEST_20_DIR/list.test"
for img in "$TEST_20_DIR"/*.png; do
    base="${img%.png}"
    if [ ! -f "${base}.lstmf" ]; then
        tesseract "$img" "$base" -l chr --psm 13 lstm.train > /dev/null 2>&1
    fi
    echo "$(realpath "${base}.lstmf")" >> "$TEST_20_DIR/list.test"
done
echo "Generated $(wc -l < "$TEST_20_DIR/list.test" | xargs) entries in $TEST_20_DIR/list.test"
