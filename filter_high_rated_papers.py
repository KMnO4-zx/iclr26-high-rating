#!/usr/bin/env python3
"""
Filter papers with average rating >= 6 and minimum rating >= 5,
sort by average rating in descending order.
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

def filter_and_sort_papers(papers_data, min_avg_rating=6, min_min_rating=5):
    """
    Filter papers based on rating criteria and sort by average rating.

    Args:
        papers_data: List of paper dictionaries
        min_avg_rating: Minimum average rating required (default: 6)
        min_min_rating: Minimum individual rating required (default: 5)

    Returns:
        Filtered and sorted list of papers
    """
    filtered_papers = []

    for paper in papers_data:
        # Check if paper has rating information
        if 'avg_rating' not in paper or paper['avg_rating'] is None:
            continue

        if 'min_rating' not in paper or paper['min_rating'] is None:
            continue

        # Apply filtering criteria
        avg_rating = paper['avg_rating']
        min_rating = paper['min_rating']

        if avg_rating >= min_avg_rating and min_rating >= min_min_rating:
            filtered_papers.append(paper)

    # Sort by average rating in descending order
    filtered_papers.sort(key=lambda x: x['avg_rating'], reverse=True)

    return filtered_papers

def main():
    # File paths
    input_file = 'iclr26_all_papers_with_ratings.json'
    output_file = 'high_rated_papers.json'

    print("Loading papers data...")
    papers_data = load_json_file(input_file)
    print(f"Loaded {len(papers_data)} papers")

    print("Filtering papers with avg_rating >= 6 and min_rating >= 5...")
    filtered_papers = filter_and_sort_papers(papers_data, min_avg_rating=6, min_min_rating=5)

    print(f"Found {len(filtered_papers)} papers meeting the criteria")

    if filtered_papers:
        print("\nTop 10 papers by average rating:")
        print("-" * 80)
        for i, paper in enumerate(filtered_papers[:10], 1):
            print(f"{i:2d}. {paper['title'][:80]}")
            print(f"    Paper ID: {paper['paper_id']}")
            print(f"    Avg Rating: {paper['avg_rating']:.2f}, Min Rating: {paper['min_rating']}")
            print(f"    Ratings: {paper['ratings']}")
            print()

        print(f"Saving filtered papers to {output_file}...")
        save_json_file(output_file, filtered_papers)

        # Also save a summary CSV for easy viewing
        csv_output = "high_rated_papers_summary.csv"
        with open(csv_output, 'w', encoding='utf-8') as f:
            f.write("Rank,Paper ID,Title,Average Rating,Min Rating,Max Rating,Reviewer Count\n")
            for i, paper in enumerate(filtered_papers, 1):
                title = paper['title'].replace(',', ';')  # Replace commas for CSV compatibility
                f.write(f"{i},{paper['paper_id']},\"{title}\",{paper['avg_rating']:.2f},{paper['min_rating']},{paper['max_rating']},{paper['reviewer_count']}\n")

        print(f"Also saved summary to {csv_output}")

    else:
        print("No papers found meeting the criteria")

if __name__ == "__main__":
    main()