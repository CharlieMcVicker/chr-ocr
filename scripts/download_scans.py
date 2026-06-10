#!/usr/bin/env python3
import os
import re
import sys
import subprocess

def parse_url_line(line):
    # Strip whitespace
    line = line.strip()
    if not line:
        return None
        
    # Match the base URL pattern, ignoring any trailing debugger eval statements or extra text
    # e.g., https://gahistoricnewspapers.galileo.usg.edu/lccn/sn83020866/1828-02-21/ed-1/seq-1/
    match = re.match(r'(https://[^\s/]+/lccn/[^/\s]+/\d{4}-\d{2}-\d{2}/ed-\d+/)', line)
    if not match:
        return None
        
    base_url = match.group(1)
    
    # Extract date and edition for folder structuring
    date_match = re.search(r'/(\d{4}-\d{2}-\d{2})/(ed-\d+)/', base_url)
    if date_match:
        date_str = date_match.group(1)
        ed_str = date_match.group(2)
    else:
        date_str = "unknown"
        ed_str = "ed-1"
        
    return {
        "base_url": base_url,
        "date": date_str,
        "edition": ed_str
    }

def download_scans(urls_file, output_dir="scans"):
    if not os.path.exists(urls_file):
        print(f"Error: URL file '{urls_file}' not found.")
        sys.exit(1)
        
    with open(urls_file, "r") as f:
        lines = f.readlines()
        
    issues = []
    for line in lines:
        parsed = parse_url_line(line)
        if parsed and parsed not in issues:
            issues.append(parsed)
            
    print(f"Parsed {len(issues)} unique issues to download from {urls_file}.")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for issue in issues:
        date = issue["date"]
        ed = issue["edition"]
        base_url = issue["base_url"]
        
        issue_dir = os.path.join(output_dir, date)
        os.makedirs(issue_dir, exist_ok=True)
        
        print(f"\nProcessing issue: {date} ({ed})")
        seq = 1
        while True:
            filename = f"seq-{seq}.jp2"
            file_url = f"{base_url}seq-{seq}.jp2"
            dest_path = os.path.join(issue_dir, filename)
            
            if os.path.exists(dest_path):
                print(f"  [Skipped] {filename} (already exists)")
                seq += 1
                continue
                
            print(f"  Downloading {filename} from {file_url} ...", end="", flush=True)
            
            # Run curl with --fail to get non-zero exit status on HTTP errors (e.g. 404, 403, 500)
            cmd = ["curl", "-f", "-s", "-L", "-o", dest_path, file_url]
            res = subprocess.run(cmd)
            
            if res.returncode == 0:
                print(" Done.")
            else:
                # Remove partially downloaded file or empty file if curl created one on failure
                if os.path.exists(dest_path):
                    try:
                        os.remove(dest_path)
                    except Exception:
                        pass
                print(f" Failed with exit code {res.returncode}. Stopping sequence for this issue.")
                break
                
            seq += 1

if __name__ == "__main__":
    urls_file = "foo.txt"
    if len(sys.argv) > 1:
        urls_file = sys.argv[1]
        
    download_scans(urls_file)
