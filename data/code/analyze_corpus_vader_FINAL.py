"""
VADER Sentiment Analysis - Full Corpus Analysis
Week 3 - Batch processing all 28 political speeches

This script:
1. Loads all speeches from the corpus
2. Runs VADER sentiment analysis on each
3. Calculates statistics by speaker, party, country, year
4. Generates visualizations comparing populist vs mainstream
5. Exports results for further analysis

IMPORTANT NOTE ABOUT METRICS:
- overall_compound: VADER score for entire speech as one text (can max out at ±1.0 for long texts)
- sentence_mean: Average of all sentence-level scores (MORE ACCURATE for long speeches)
- For analysis, USE sentence_mean as your primary metric!
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os
import json
import csv
from collections import defaultdict
import statistics

def get_column_value(row, column_name):
    """
    Get value from row, handling case-insensitive column names
    """
    # Try exact match first
    if column_name in row:
        return row[column_name]

    # Try case-insensitive match
    for key in row.keys():
        if key.lower() == column_name.lower():
            return row[key]

    # Return 'Unknown' if not found
    return 'Unknown'

def convert_to_cleaned_filename(original_filename):
    """
    Convert metadata filename to preprocessed filename
    e.g., 'farage_2016.txt' -> 'farage_2016_cleaned.txt'
    """
    if original_filename.endswith('.txt'):
        # Remove .txt and add _cleaned.txt
        base = original_filename[:-4]
        return f"{base}_cleaned.txt"
    else:
        # If no .txt extension, just add _cleaned.txt
        return f"{original_filename}_cleaned.txt"

def extract_year_from_date(date_string):
    """
    Extract year from date in DD/MM/YYYY format
    e.g., '02/09/2004' -> '2004'
    """
    if not date_string or date_string == 'Unknown':
        return 'Unknown'

    try:
        # Split by / and take last part (year)
        parts = date_string.split('/')
        if len(parts) == 3:
            return parts[2]  # YYYY
    except:
        pass

    return 'Unknown'

def load_corpus_metadata(metadata_file):
    """
    Load the metadata CSV that tracks all speeches
    Handles case-insensitive column names and converts filenames to _cleaned.txt format
    """
    metadata = []

    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        print(f"Found columns in CSV: {', '.join(reader.fieldnames)}")
        print()

        for row in reader:
            # Extract values with case-insensitive matching
            original_filename = get_column_value(row, 'filename')
            cleaned_filename = convert_to_cleaned_filename(original_filename)

            # Get date and extract year
            date_str = get_column_value(row, 'date')
            year = extract_year_from_date(date_str)

            entry = {
                'filename': cleaned_filename,  # Use cleaned filename
                'original_filename': original_filename,  # Keep original for reference
                'speaker': get_column_value(row, 'speaker'),
                'party': get_column_value(row, 'party'),
                'country': get_column_value(row, 'country'),
                'year': year,  # Extracted from Date column
                'date': date_str,
                'category': get_column_value(row, 'category'),
            }
            metadata.append(entry)

    print(f"✓ Loaded metadata for {len(metadata)} speeches")
    print(f"✓ Converted filenames to _cleaned.txt format")
    print(f"✓ Extracted years from dates")
    return metadata

def analyze_speech_sentiment(text, analyzer):
    """
    Analyze sentiment of a full speech
    Returns overall scores plus sentence-level statistics
    """
    # Overall text score
    overall_scores = analyzer.polarity_scores(text)

    # Sentence-level analysis
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    sentence_scores = []

    for sent in sentences:
        if len(sent) > 10:  # Skip very short fragments
            scores = analyzer.polarity_scores(sent)
            sentence_scores.append(scores['compound'])

    # Calculate statistics
    if sentence_scores:
        mean_compound = statistics.mean(sentence_scores)
        median_compound = statistics.median(sentence_scores)
        stdev_compound = statistics.stdev(sentence_scores) if len(sentence_scores) > 1 else 0

        # Count sentiment categories
        positive = sum(1 for s in sentence_scores if s >= 0.05)
        neutral = sum(1 for s in sentence_scores if -0.05 < s < 0.05)
        negative = sum(1 for s in sentence_scores if s <= -0.05)
    else:
        mean_compound = median_compound = stdev_compound = 0
        positive = neutral = negative = 0

    return {
        'overall_compound': overall_scores['compound'],
        'overall_pos': overall_scores['pos'],
        'overall_neu': overall_scores['neu'],
        'overall_neg': overall_scores['neg'],
        'sentence_mean': mean_compound,
        'sentence_median': median_compound,
        'sentence_stdev': stdev_compound,
        'num_sentences': len(sentence_scores),
        'num_positive': positive,
        'num_neutral': neutral,
        'num_negative': negative,
        'pct_positive': (positive / len(sentence_scores) * 100) if sentence_scores else 0,
        'pct_neutral': (neutral / len(sentence_scores) * 100) if sentence_scores else 0,
        'pct_negative': (negative / len(sentence_scores) * 100) if sentence_scores else 0,
    }

def analyze_corpus(corpus_dir, metadata_file, output_dir):
    """
    Main function to analyze entire corpus
    """
    print("=" * 80)
    print("VADER SENTIMENT ANALYSIS - FULL CORPUS")
    print("=" * 80)
    print()

    # Initialize
    analyzer = SentimentIntensityAnalyzer()
    metadata = load_corpus_metadata(metadata_file)

    # Results storage
    all_results = []

    # Process each speech
    print("\nAnalyzing speeches...")
    for i, entry in enumerate(metadata, 1):
        filename = entry['filename']
        filepath = os.path.join(corpus_dir, filename)

        # Check if file exists
        if not os.path.exists(filepath):
            print(f"  ⚠ File not found: {filename}")
            print(f"     Looking for: {filepath}")
            continue

        # Load speech text
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Analyze
        scores = analyze_speech_sentiment(text, analyzer)

        # Combine with metadata
        result = {
            'filename': filename,
            'original_filename': entry.get('original_filename', filename),
            'speaker': entry.get('speaker', 'Unknown'),
            'party': entry.get('party', 'Unknown'),
            'country': entry.get('country', 'Unknown'),
            'year': entry.get('year', 'Unknown'),
            'date': entry.get('date', 'Unknown'),
            'category': entry.get('category', 'Unknown'),  # populist vs mainstream
            **scores
        }

        all_results.append(result)

        # Use sentence_mean as the primary metric (more accurate for long texts)
        primary_score = scores['sentence_mean']
        print(f"  {i:2d}. {entry.get('speaker', 'Unknown'):20s} ({entry.get('year', 'Unknown')}) → Sentiment: {primary_score:+.3f}")

    print(f"\n✓ Analyzed {len(all_results)} speeches")

    # Export detailed results
    export_results(all_results, output_dir)

    # Generate summary statistics
    generate_summary_stats(all_results, output_dir)

    return all_results

def export_results(results, output_dir):
    """Export detailed results to CSV"""

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'vader_sentiment_results.csv')

    if not results:
        print("No results to export")
        return

    # Write CSV
    fieldnames = list(results[0].keys())

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Detailed results exported to: {output_file}")

def generate_summary_stats(results, output_dir):
    """Generate summary statistics by category"""

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    # Group by category (populist vs mainstream)
    by_category = defaultdict(list)
    for r in results:
        category = r['category']
        # Use sentence_mean - more accurate for long speeches
        by_category[category].append(r['sentence_mean'])

    # Overall statistics
    print("\n1. BY POLITICAL CATEGORY:")
    print("-" * 80)

    for category in sorted(by_category.keys()):
        scores = by_category[category]
        if scores:
            print(f"\n{category.upper()}:")
            print(f"  N = {len(scores)}")
            print(f"  Mean compound:   {statistics.mean(scores):+.3f}")
            print(f"  Median compound: {statistics.median(scores):+.3f}")
            print(f"  Std dev:         {statistics.stdev(scores):.3f}" if len(scores) > 1 else "  Std dev:         N/A")
            print(f"  Range:           {min(scores):+.3f} to {max(scores):+.3f}")

    # By country
    by_country = defaultdict(list)
    for r in results:
        by_country[r['country']].append(r['sentence_mean'])

    print("\n2. BY COUNTRY:")
    print("-" * 80)
    for country in sorted(by_country.keys()):
        scores = by_country[country]
        if scores:
            print(f"{country}: Mean = {statistics.mean(scores):+.3f}, N = {len(scores)}")

    # By speaker
    by_speaker = defaultdict(list)
    for r in results:
        by_speaker[r['speaker']].append(r['sentence_mean'])

    print("\n3. BY SPEAKER (Top 10 by speech count):")
    print("-" * 80)
    speaker_stats = []
    for speaker, scores in by_speaker.items():
        speaker_stats.append({
            'speaker': speaker,
            'count': len(scores),
            'mean': statistics.mean(scores)
        })

    speaker_stats.sort(key=lambda x: x['count'], reverse=True)
    for s in speaker_stats[:10]:
        print(f"{s['speaker']:20s}: Mean = {s['mean']:+.3f}, N = {s['count']}")

    # Time trends
    by_year = defaultdict(list)
    for r in results:
        try:
            year = int(r['year'])
            by_year[year].append(r['sentence_mean'])
        except (ValueError, KeyError):
            pass

    if by_year:
        print("\n4. TRENDS OVER TIME:")
        print("-" * 80)
        for year in sorted(by_year.keys()):
            scores = by_year[year]
            print(f"{year}: Mean = {statistics.mean(scores):+.3f}, N = {len(scores)}")

    # Export summary
    summary_file = os.path.join(output_dir, 'vader_summary_statistics.txt')
    with open(summary_file, 'w') as f:
        f.write("VADER SENTIMENT ANALYSIS - SUMMARY STATISTICS\n")
        f.write("=" * 80 + "\n\n")

        f.write("BY CATEGORY:\n")
        for category in sorted(by_category.keys()):
            scores = by_category[category]
            if scores:
                f.write(f"\n{category}:\n")
                f.write(f"  N = {len(scores)}\n")
                f.write(f"  Mean: {statistics.mean(scores):+.3f}\n")
                f.write(f"  Median: {statistics.median(scores):+.3f}\n")
                if len(scores) > 1:
                    f.write(f"  Std Dev: {statistics.stdev(scores):.3f}\n")

    print(f"\n✓ Summary statistics saved to: {summary_file}")
    print("=" * 80)

def main():
    """
    Main execution function

    BEFORE RUNNING: Update these paths to match your local setup
    """

    # === CONFIGURE THESE PATHS ===
    CORPUS_DIR = "/home/albere/CompLing/data/processed"  # Update this!
    METADATA_FILE = "/home/albere/CompLing/data/docs/metadata.csv"            # Update this!
    OUTPUT_DIR = "/home/albere/CompLing/data/results/vader_results"            # Update this!
    # =============================

    # Check paths exist
    if not os.path.exists(CORPUS_DIR):
        print(f"❌ ERROR: Corpus directory not found: {CORPUS_DIR}")
        print("\nPlease update the paths in the script:")
        print("  - CORPUS_DIR: Location of your processed speech .txt files")
        print("  - METADATA_FILE: Path to your metadata CSV")
        print("  - OUTPUT_DIR: Where to save results")
        return

    if not os.path.exists(METADATA_FILE):
        print(f"❌ ERROR: Metadata file not found: {METADATA_FILE}")
        return

    # Run analysis
    results = analyze_corpus(CORPUS_DIR, METADATA_FILE, OUTPUT_DIR)

    print("\n" + "=" * 80)
    print("✓ ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print(f"  1. {OUTPUT_DIR}/vader_sentiment_results.csv")
    print(f"  2. {OUTPUT_DIR}/vader_summary_statistics.txt")
    print("\nNEXT STEPS:")
    print("  1. Review the summary statistics")
    print("  2. Import the CSV into your data analysis notebook")
    print("  3. Create visualizations comparing populist vs mainstream")
    print("  4. Consider running sentence-level analysis for more detail")

if __name__ == "__main__":
    main()
