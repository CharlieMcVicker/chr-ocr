import subprocess
import os

def update_unicharset(filepath):
    print(f"Updating: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    
    # Check current size
    size = int(lines[0])
    print(f"Current count: {size}")
    
    # Check if chars already present
    present = [False, False, False]
    for idx, char in enumerate(["4 ", "[ ", "] "]):
        for line in lines[1:]:
            if line.startswith(char):
                present[idx] = True
    
    if all(present):
        print(f"Characters already present in {filepath}")
        return size

    # Update size
    new_size = size
    
    # We will generate lines based on how the starter unicharset or target unicharset is structured.
    # We'll use standard properties.
    # 4: 8 (numeric/digit property)
    # [: 16 (punctuation property)
    # ]: 16 (punctuation property)
    # Let's inspect the target unicharset vs starter unicharset.
    # Starter uses:
    # 1 8 49,69,192,255,45,128,0,66,74,173 Common 89 2 89 1	# 1 [31 ]0
    # Common has 10 parameters or 12. Let's look at standard format.
    # In target unicharset (which is from tessdata_best, simplified property):
    # 1 8 0,255,0,255,0,0,0,0,0,0 Common 89 2 89 1	# 1 [31 ]0
    #
    # We can detect whether it has 10 elements in the third field (bounding box/script info) or properties.
    # Let's just look at line 2 to see properties format.
    
    sample_line = lines[2] # e.g. Joined 7 0,255,0,255,0,0,0,0,0,0 Latin 1 ...
    fields = sample_line.split()
    has_zero_properties = "0,255,0,255" in fields[2]
    
    # Let's construct the appropriate strings:
    if has_zero_properties:
        # Target style (simple):
        char_4 = "4 8 0,255,0,255,0,0,0,0,0,0 Common {index} 2 {index} 4\t# 4 [34 ]0"
        char_open = "[ 16 0,255,0,255,0,0,0,0,0,0 Common {index} 10 {index} [\t# [ [5b ]p"
        char_close = "] 16 0,255,0,255,0,0,0,0,0,0 Common {index} 10 {index} ]\t# ] [5d ]p"
    else:
        # Starter style (complex, has learned properties/statistics from training):
        # We can use some defaults or copy close properties.
        # e.g., '3 8 0,66,196,255,84,158,0,32,103,173 Common 98 2 98 3'
        # Let's use standard default properties or dummy ones.
        char_4 = "4 8 0,66,196,255,84,158,0,32,103,173 Common {index} 2 {index} 4\t# 4 [34 ]0"
        char_open = "[ 16 14,56,131,221,17,93,0,58,38,173 Common {index} 10 {index} [\t# [ [5b ]p"
        char_close = "] 16 14,56,131,221,17,93,0,58,38,173 Common {index} 10 {index} ]\t# ] [5d ]p"
        
    added_lines = []
    if not present[0]:
        added_lines.append(char_4.format(index=new_size))
        new_size += 1
    if not present[1]:
        added_lines.append(char_open.format(index=new_size))
        new_size += 1
    if not present[2]:
        added_lines.append(char_close.format(index=new_size))
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
