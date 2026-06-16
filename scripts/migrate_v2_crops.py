import os
import json
import shutil

manifest_path = "training_data/manifest_w_lang.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Delete symlink and create directory
symlink_path = "training_data/line_crops"
if os.path.islink(symlink_path):
    os.unlink(symlink_path)
    os.makedirs(symlink_path, exist_ok=True)
    print("Replaced symlink with real directory.")

moved_count = 0
missing_count = 0

for item in manifest.values():
    filename = item["image_path"].split("/")[-1]
    src_path = os.path.join("training_data/line_crops", filename)
    dst_path = os.path.join("training_data/line_crops", filename)
    
    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        moved_count += 1
    elif not os.path.exists(dst_path):
        missing_count += 1

print(f"Moved {moved_count} files to training_data/line_crops.")
print(f"Still missing {missing_count} files.")
