import subprocess
import os

def update_unicharset(filepath):
    print(f"Updating: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    
    # Check current size
    size = int(lines[0])
    print(f"Current count: {size}")
    
    # Define the target characters and their properties
    # Each item: (char, simple_prop, complex_prop, script, direction, char_hex, char_category)
    targets = [
        ("4", "8", "8", "Common", "2", "34", "0"),
        ("[", "16", "16", "Common", "10", "5b", "p"),
        ("]", "16", "16", "Common", "10", "5d", "p"),
        ("Ꮐ", "5", "1", "Cherokee", "0", "13c0", "x"),
        ("?", "10", "16", "Common", "10", "3f", "p")
    ]
    
    # Check which characters are already present
    present = []
    for char, _, _, _, _, _, _ in targets:
        char_found = False
        for line in lines[1:]:
            if line.startswith(char + " "):
                char_found = True
                break
        present.append(char_found)
        
    if all(present):
        print(f"All target characters already present in {filepath}")
        return size

    sample_line = lines[2] # e.g. Joined 7 0,255,0,255,0,0,0,0,0,0 Latin 1 ...
    fields = sample_line.split()
    has_zero_properties = "0,255,0,255" in fields[2]
    
    new_size = size
    added_lines = []
    
    for idx, (char, simple_prop, complex_prop, script, direction, char_hex, char_category) in enumerate(targets):
        if present[idx]:
            continue
            
        if has_zero_properties:
            # Target style (simple):
            prop = simple_prop
            bbox = "0,255,0,255,0,0,0,0,0,0"
            category = "A" if script == "Cherokee" else char_category
        else:
            # Starter style (complex):
            prop = complex_prop
            if char == "4":
                bbox = "0,66,196,255,84,158,0,32,103,173"
            elif char in ["[", "]"]:
                bbox = "14,56,131,221,17,93,0,58,38,173"
            elif char == "Ꮐ":
                bbox = "64,64,255,255,174,190,8,27,195,211"
            elif char == "?":
                bbox = "41,67,216,255,11,87,0,71,50,173"
            else:
                bbox = "0,255,0,255,0,0,0,0,0,0"
            category = char_category
            
        line_str = f"{char} {prop} {bbox} {script} {new_size} {direction} {new_size} {char}\t# {char} [{char_hex} ]{category}"
        added_lines.append(line_str)
        new_size += 1
        
    lines[0] = str(new_size)
    lines.extend(added_lines)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Updated {filepath} to count: {new_size}")
    return new_size

def update_traineddata(traineddata_path, unicharset_path, unicharset_type):
    # unicharset_type can be lstm-unicharset or unicharset
    print(f"Updating {traineddata_path} with {unicharset_path} as {unicharset_type}")
    # combine_tessdata -o traineddata_file input_component_file
    # BUT combine_tessdata needs the input file to be named correctly or we can pass it.
    # Wait! combine_tessdata -o requires the file to be named appropriately in the CWD, or does it take the exact filepath?
    # "combine_tessdata -o eng.traineddata eng.unicharset"
    # It replaces the component. Let's make a temp copy in a directory if needed, or run it in that dir.
    dir_name = os.path.dirname(traineddata_path)
    base_traineddata = os.path.basename(traineddata_path)
    
    # Copy unicharset to the same directory with the expected component name if needed, or just pass path
    # Actually, combine_tessdata -o traineddata_file input_component_file
    # Let's run it directly.
    subprocess.run(
        ["combine_tessdata", "-o", base_traineddata, os.path.basename(unicharset_path)],
        cwd=dir_name,
        check=True
    )
    
    # Check components
    res = subprocess.run(
        ["combine_tessdata", "-d", base_traineddata],
        cwd=dir_name,
        capture_output=True,
        text=True,
        check=True
    )
    print(res.stdout)

def main():
    # 1. Update files
    update_unicharset("dataset/model/chr.lstm-unicharset")
    update_unicharset("training_data/dataset/model/starter/chr/chr.lstm-unicharset")
    update_unicharset("training_data/dataset/model/starter/chr/chr.unicharset")
    
    # 2. Update traineddata
    update_traineddata("dataset/model/chr.traineddata", "dataset/model/chr.lstm-unicharset", "lstm-unicharset")
    update_traineddata("training_data/dataset/model/starter/chr/chr.traineddata", "training_data/dataset/model/starter/chr/chr.lstm-unicharset", "lstm-unicharset")
    update_traineddata("training_data/dataset/model/starter/chr/chr.traineddata", "training_data/dataset/model/starter/chr/chr.unicharset", "unicharset")
    
    print("All tasks completed successfully!")

if __name__ == "__main__":
    main()
