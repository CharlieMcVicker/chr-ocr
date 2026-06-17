import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for the site
BASE_URL = "https://www.cherokeedictionary.net/cnt/"

# Headers to prevent 403 Forbidden errors
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

import json

def scrape_book(book_number_str, output_dir="training_data/cnt"):
    """
    Scrapes a single book (e.g. '01' for Matthew) from the Cherokee New Testament Online.
    
    Args:
        book_number_str: String representation of book, e.g. '01' or '02'
        output_dir: Root output directory to save pages, images, and text transcriptions.
    """
    print(f"Starting spike scrape for book {book_number_str}...")
    
    book_index_url = urljoin(BASE_URL, f"{book_number_str}.html")
    
    # Create output directories
    book_dir = os.path.join(output_dir, f"book_{book_number_str}")
    images_dir = os.path.join(book_dir, "images")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(book_dir, exist_ok=True)
    
    # 1. Fetch the book index page to get chapters
    response = requests.get(book_index_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch book index: {book_index_url} (Status: {response.status_code})")
        return
        
    soup = BeautifulSoup(response.text, "lxml")
    
    # Find all chapter links. Format: e.g. <a href="0101.html">Chapter 1</a>
    chapter_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Match standard chapter pattern e.g., 0101.html, 0102.html, etc.
        if re.match(rf"^{book_number_str}\d+\.html$", href):
            chapter_links.append(href)
            
    print(f"Found {len(chapter_links)} chapters in book {book_number_str}.")
    
    # For a spike, let's scrape a single chapter first (e.g. Chapter 1)
    if not chapter_links:
        print("No chapter links found!")
        return
        
    target_chapter = chapter_links[0]
    print(f"Spiking on chapter: {target_chapter}")
    
    chapter_url = urljoin(BASE_URL, target_chapter)
    resp = requests.get(chapter_url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Failed to fetch chapter page: {chapter_url} (Status: {resp.status_code})")
        return
        
    # Use resp.content decoded with utf-8 to avoid requests default ISO-8859-1 interpretation
    chap_soup = BeautifulSoup(resp.content.decode('utf-8', errors='ignore'), "lxml")
    
    # Find all tables with border=1 or iterate tables to extract verse information
    tables = chap_soup.find_all("table", border=True)
    print(f"Found {len(tables)} tables (verses) in chapter {target_chapter}.")
    
    metadata = {}
    
    for i, table in enumerate(tables, 1):
        # In each table:
        # row 0: image link + image preview (e.g., 011401.png)
        # row 1: English transcription
        # row 2: Cherokee Syllabary transcription
        # row 3: Phonetic/Transliterated transcription
        rows = table.find_all("tr")
        if len(rows) < 4:
            print(f"Table {i} has unexpected format (only {len(rows)} rows). Skipping.")
            continue
            
        # Extract Image url
        img_tag = rows[0].find("img")
        if not img_tag or not img_tag.get("src"):
            print(f"Table {i} row 0 does not contain img src. Skipping.")
            continue
            
        img_filename = img_tag["src"]
        img_url = urljoin(BASE_URL, img_filename)
        
        # Extract Text
        # The text inside <th> is the content
        eng_text = rows[1].get_text(strip=True)
        chr_text = rows[2].get_text(strip=True)
        pho_text = rows[3].get_text(strip=True)
        
        # Download Image
        img_dest = os.path.join(images_dir, img_filename)
        print(f"Downloading {img_filename} ... ", end="")
        img_resp = requests.get(img_url, headers=HEADERS)
        if img_resp.status_code == 200:
            with open(img_dest, "wb") as f:
                f.write(img_resp.content)
            print("Done.")
        else:
            print(f"Failed ({img_resp.status_code}).")
            
        base_name = os.path.splitext(img_filename)[0]
        metadata[base_name] = {
            "image_path": os.path.join("images", img_filename),
            "english": eng_text,
            "cherokee": chr_text,
            "phonetic": pho_text
        }
        
        time.sleep(0.5)  # Be polite

    metadata_path = os.path.join(book_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Saved all transcripts to {metadata_path}")

if __name__ == "__main__":
    scrape_book("01")
