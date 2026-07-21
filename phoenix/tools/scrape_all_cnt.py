import os
import re
import time
import requests
import json
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.cherokeedictionary.net/cnt/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_book(book_number_str, output_dir="training_data/cnt"):
    print(f"\n--- Starting scrape for book {book_number_str} ---")
    book_index_url = urljoin(BASE_URL, f"{book_number_str}.html")
    
    book_dir = os.path.join(output_dir, f"book_{book_number_str}")
    images_dir = os.path.join(book_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    response = requests.get(book_index_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch book index: {book_index_url} (Status: {response.status_code})")
        return
        
    soup = BeautifulSoup(response.text, "html.parser")
    chapter_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.match(rf"^{book_number_str}\d+\.html$", href):
            chapter_links.append(href)
            
    # Remove duplicates preserving order
    chapter_links = list(dict.fromkeys(chapter_links))
    print(f"Found {len(chapter_links)} chapters in book {book_number_str}.")
    
    metadata = {}
    metadata_path = os.path.join(book_dir, "metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}

    for chap_idx, chapter_link in enumerate(chapter_links, 1):
        print(f"Scraping chapter {chap_idx}/{len(chapter_links)}: {chapter_link}")
        chapter_url = urljoin(BASE_URL, chapter_link)
        
        retries = 3
        resp = None
        for attempt in range(retries):
            try:
                resp = requests.get(chapter_url, headers=HEADERS, timeout=15)
                if resp.status_code == 200:
                    break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}")
                time.sleep(2)
                
        if not resp or resp.status_code != 200:
            print(f"  Failed to fetch chapter page: {chapter_url}")
            continue
            
        chap_soup = BeautifulSoup(resp.content.decode('utf-8', errors='ignore'), "html.parser")
        tables = chap_soup.find_all("table", border=True)
        print(f"  Found {len(tables)} verses in chapter.")
        for i, table in enumerate(tables, 1):
            ths = table.find_all("th")
            if len(ths) < 4:
                continue
                
            img_tag = ths[0].find("img")
            if not img_tag or not img_tag.get("src"):
                continue
                
            img_filename = img_tag["src"]
            img_url = urljoin(BASE_URL, img_filename)
            
            def get_direct_text(el):
                try:
                    nodes = el.find_all(string=True, recursive=False)
                except TypeError:
                    nodes = el.find_all(text=True, recursive=False)
                return "".join(nodes).strip()
                
            eng_text = get_direct_text(ths[1])
            chr_text = get_direct_text(ths[2])
            pho_text = get_direct_text(ths[3])
            
            base_name = os.path.splitext(img_filename)[0]
            
            # Download image if not already downloaded
            img_dest = os.path.join(images_dir, img_filename)
            if not os.path.exists(img_dest):
                img_resp = None
                for attempt in range(3):
                    try:
                        img_resp = requests.get(img_url, headers=HEADERS, timeout=15)
                        if img_resp.status_code == 200:
                            with open(img_dest, "wb") as f:
                                f.write(img_resp.content)
                            break
                    except Exception as e:
                        time.sleep(1)
                if not img_resp or img_resp.status_code != 200:
                    print(f"  Failed to download image {img_filename}")
            
            metadata[base_name] = {
                "image_path": os.path.join("images", img_filename),
                "english": eng_text,
                "cherokee": chr_text,
                "phonetic": pho_text
            }
            
        # Be polite between chapters
        time.sleep(0.5)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Saved book {book_number_str} transcripts to {metadata_path}")

def main():
    parser = argparse.ArgumentParser(description="Scrape Cherokee New Testament Online.")
    parser.add_argument("--books", default="01-27", help="Range or comma-separated list of books to scrape, e.g. 01-27 or 01,02")
    parser.add_argument("--output-dir", default="training_data/cnt", help="Root directory for scraped books")
    args = parser.parse_args()
    
    # Parse books to scrape
    books_to_scrape = []
    if "-" in args.books:
        start, end = map(int, args.books.split("-"))
        books_to_scrape = [f"{i:02d}" for i in range(start, end + 1)]
    else:
        books_to_scrape = [b.strip() for b in args.books.split(",") if b.strip()]
        
    for book in books_to_scrape:
        scrape_book(book, args.output_dir)

if __name__ == "__main__":
    main()
