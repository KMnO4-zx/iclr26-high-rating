#!/usr/bin/env python3
"""
Add rating information from iclr26_ratings.json to iclr26_all_papers.json
"""

import json
import sys
from pathlib import Path

def load_json_file(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

def save_json_file(filepath, data):
    """Save JSON data to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        sys.exit(1)

def create_ratings_dict(ratings_data):
    """Create a dictionary mapping paper_id to rating information"""
    ratings_dict = {}
    for item in ratings_data:
        paper_id = item['paper_id']
        ratings_dict[paper_id] = {
            'ratings': item['ratings'],
            'min_rating': item['min_rating'],
            'max_rating': item['max_rating'],
            'avg_rating': item['avg_rating'],
            'reviewer_count': item['reviewer_count']
        }
    return ratings_dict

def add_ratings_to_papers(papers_data, ratings_dict):
    """Add rating information to papers"""
    updated_count = 0
    missing_count = 0

    for paper in papers_data:
        paper_id = paper['paper_id']
        if paper_id in ratings_dict:
            # Add rating information to the paper
            paper.update(ratings_dict[paper_id])
            updated_count += 1
        else:
            # Add empty rating fields for papers without ratings
            paper.update({
                'ratings': [],
                'min_rating': None,
                'max_rating': None,
                'avg_rating': None,
                'reviewer_count': 0
            })
            missing_count += 1

    return papers_data, updated_count, missing_count

def main():
    # File paths
    ratings_file = 'iclr26_ratings.json'
    papers_file = 'iclr26_all_papers.json'
    output_file = 'iclr26_all_papers_with_ratings.json'

    print("Loading rating data...")
    ratings_data = load_json_file(ratings_file)
    print(f"Loaded {len(ratings_data)} rating records")

    print("Loading papers data...")
    papers_data = load_json_file(papers_file)
    print(f"Loaded {len(papers_data)} papers")

    print("Creating ratings dictionary...")
    ratings_dict = create_ratings_dict(ratings_data)
    print(f"Created dictionary with {len(ratings_dict)} unique paper ratings")

    print("Adding ratings to papers...")
    updated_papers, updated_count, missing_count = add_ratings_to_papers(papers_data, ratings_dict)

    print(f"Processing complete:")
    print(f"  - Papers with ratings added: {updated_count}")
    print(f"  - Papers without ratings: {missing_count}")
    print(f"  - Total papers: {len(updated_papers)}")

    print(f"Saving updated papers to {output_file}...")
    save_json_file(output_file, updated_papers)

    print("Done!")

if __name__ == "__main__":
    main()