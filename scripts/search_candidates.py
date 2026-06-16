#!/usr/bin/env python3
import argparse
import sys
import os

# Add the project root to sys.path so we can import inference
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from inference import build_db, search_db

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite FTS5 LSTM OCR Candidate Search")
    parser.add_argument("--build", action="store_true", help="Build the search index database")
    parser.add_argument("--limit", type=int, default=100, help="Number of lines to index during build")
    parser.add_argument("--search", type=str, help="Search for a term in the candidates database")
    
    args = parser.parse_args()
    
    if args.build:
        build_db(args.limit)
    elif args.search:
        search_db(args.search)
    else:
        parser.print_help()
