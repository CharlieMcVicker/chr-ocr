import json

paths = ["training_data_v2/manifest_w_lang.json", "training_data_v2/manifest.json"]

for path in paths:
    with open(path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    keys_to_remove = []
    for k, v in manifest.items():
        if v.get("ftm_ocr") == "Error" or v.get("predicted_lang") == "Error":
            keys_to_remove.append(k)
            
    for k in keys_to_remove:
        del manifest[k]
        
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"Removed {len(keys_to_remove)} error entries from {path}")
