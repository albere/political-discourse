#!/usr/bin/env python3
"""
MASTER ANALYSIS SCRIPT
Complete corpus analysis in one command

Runs:
1. All 6 linguistic features (VADER, anti-elite, crisis, certainty, pronouns, readability)
2. N-gram analysis (bigrams and trigrams)
3. Statistical tests (t-tests, effect sizes)
4. Generates summary report

Usage: python RUN_COMPLETE_ANALYSIS.py
"""

import sys
import os
import csv
import statistics
from collections import defaultdict
from datetime import datetime

# === YOUR PROJECT PATHS ===
CORPUS_DIR = "/home/albere/compling/data/processed"
METADATA_FILE = "/home/albere/compling/data/docs/metadata.csv"
RESULTS_BASE = "/home/albere/compling/data/results"

# Import all analyzers
print("Importing analyzers...")
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from anti_elite_detector import AntiEliteDetector
    from crisis_detector import CrisisDetector
    from certainty_detector import CertaintyDetector
    from pronoun_analyzer import PronounAnalyzer
    from readability_analyzer import ReadabilityAnalyzer
    from ngram_analyzer import ImprovedNgramAnalyzer
    from statistical_testing import StatisticalTester
    print("✓ All analyzers imported successfully\n")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all detector .py files are in the same directory")
    sys.exit(1)


def load_metadata(metadata_file):
    """Load metadata with case-insensitive column handling"""
    metadata = []
    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {}
            for key in row.keys():
                entry[key.lower()] = row[key]
            metadata.append(entry)
    return metadata


def run_linguistic_features():
    """
    PART 1: Run all 6 linguistic features
    """
    print("=" * 80)
    print("PART 1: LINGUISTIC FEATURES ANALYSIS")
    print("=" * 80)
    print()

    # Check paths
    if not os.path.exists(CORPUS_DIR):
        print(f"❌ Corpus directory not found: {CORPUS_DIR}")
        return None

    if not os.path.exists(METADATA_FILE):
        print(f"❌ Metadata file not found: {METADATA_FILE}")
        return None

    # Initialize all analyzers
    print("Initializing analyzers...")
    vader = SentimentIntensityAnalyzer()
    anti_elite = AntiEliteDetector()
    crisis = CrisisDetector()
    certainty = CertaintyDetector()
    pronoun = PronounAnalyzer()
    readability = ReadabilityAnalyzer()
    print("✓ All analyzers ready\n")

    # Load metadata
    metadata = load_metadata(METADATA_FILE)
    print(f"✓ Loaded metadata for {len(metadata)} speeches\n")

    # Storage for all results
    all_results = []

    print("=" * 80)
    print("ANALYZING SPEECHES...")
    print("=" * 80)

    # Process each speech
    for i, entry in enumerate(metadata, 1):
        filename_raw = entry.get('filename', '')
        if not filename_raw.endswith('_cleaned.txt'):
            filename = filename_raw.replace('.txt', '_cleaned.txt')
        else:
            filename = filename_raw

        filepath = os.path.join(CORPUS_DIR, filename)

        if not os.path.exists(filepath):
            print(f"  ⚠ File not found: {filename}")
            continue

        # Load text
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        speaker = entry.get('speaker', 'Unknown')
        print(f"\n{i:2d}. {speaker:20s} ({filename})")

        # Run all analyses
        print("    Running: ", end="")

        # VADER Sentiment (sentence-level)
        print("sentiment...", end=" ", flush=True)
        sentences = text.split('.')
        sentence_scores = [vader.polarity_scores(s)['compound'] for s in sentences if s.strip()]
        vader_compound = sum(sentence_scores) / len(sentence_scores) if sentence_scores else 0
        vader_pos = vader.polarity_scores(text)['pos']
        vader_neg = vader.polarity_scores(text)['neg']
        vader_neu = vader.polarity_scores(text)['neu']

        # Anti-elite
        print("anti-elite...", end=" ", flush=True)
        elite_results = anti_elite.analyze(text)

        # Crisis
        print("crisis...", end=" ", flush=True)
        crisis_results = crisis.analyze(text)

        # Certainty
        print("certainty...", end=" ", flush=True)
        certainty_results = certainty.analyze(text)

        # Pronouns
        print("pronouns...", end=" ", flush=True)
        pronoun_results = pronoun.analyze(text)

        # Readability
        print("readability...", end=" ", flush=True)
        read_results = readability.analyze(text)

        print("✓")

        # Compile all results
        result = {
            # Metadata
            'filename': filename,
            'speaker': speaker,
            'country': entry.get('country', 'Unknown'),
            'year': entry.get('date', '')[-4:] if entry.get('date') else 'Unknown',
            'category': entry.get('category', 'Unknown'),
            'word_count': elite_results['word_count'],

            # VADER Sentiment
            'vader_compound': vader_compound,
            'vader_positive': vader_pos,
            'vader_negative': vader_neg,
            'vader_neutral': vader_neu,

            # Anti-elite
            'anti_elite_count': elite_results['total_anti_elite_count'],
            'anti_elite_density': elite_results['anti_elite_density'],

            # Crisis
            'crisis_count': crisis_results['total_crisis_count'],
            'crisis_density': crisis_results['crisis_density'],

            # Certainty
            'certainty_count': certainty_results['total_certainty_count'],
            'certainty_density': certainty_results['certainty_density'],
            'hedging_count': certainty_results['hedging_count'],
            'hedging_density': certainty_results['hedging_density'],
            'certainty_hedging_ratio': certainty_results['certainty_hedging_ratio'],

            # Pronouns
            'we_count': pronoun_results['we_count'],
            'they_count': pronoun_results['they_count'],
            'we_density': pronoun_results['we_density'],
            'they_density': pronoun_results['they_density'],
            'we_they_ratio': pronoun_results['we_they_ratio'],

            # Readability
            'flesch_reading_ease': read_results['flesch_reading_ease'],
            'flesch_kincaid_grade': read_results['flesch_kincaid_grade'],
            'avg_sentence_length': read_results['avg_sentence_length'],
            'difficult_words_pct': read_results['difficult_words_pct'],
        }

        all_results.append(result)

    print(f"\n✓ Analyzed {len(all_results)} speeches")

    # Export results
    output_file = os.path.join(RESULTS_BASE, 'all_features_combined.csv')

    # Round all numeric values to 2 decimal places
    rounded_results = []
    for result in all_results:
        rounded = {}
        for key, value in result.items():
            if isinstance(value, float):
                rounded[key] = round(value, 2)
            else:
                rounded[key] = value
        rounded_results.append(rounded)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rounded_results[0].keys()))
        writer.writeheader()
        writer.writerows(rounded_results)

    print(f"\n✓ Results saved to: {output_file}")

    return rounded_results


def run_ngram_analysis():
    """
    PART 2: N-gram analysis
    """
    print("\n\n" + "=" * 80)
    print("PART 2: N-GRAM ANALYSIS")
    print("=" * 80)
    print()

    # Load metadata
    metadata = load_metadata(METADATA_FILE)
    print(f"✓ Loaded metadata for {len(metadata)} speeches\n")

    # Separate by category
    populist_texts = []
    mainstream_texts = []

    print("Loading speeches...")
    for entry in metadata:
        filename_raw = entry.get('filename', '')
        if not filename_raw.endswith('_cleaned.txt'):
            filename = filename_raw.replace('.txt', '_cleaned.txt')
        else:
            filename = filename_raw

        filepath = os.path.join(CORPUS_DIR, filename)

        if not os.path.exists(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        category = entry.get('category', 'Unknown')
        if category == 'Populist':
            populist_texts.append(text)
        elif category == 'Mainstream':
            mainstream_texts.append(text)

    print(f"✓ Loaded {len(populist_texts)} Populist speeches")
    print(f"✓ Loaded {len(mainstream_texts)} Mainstream speeches")

    # Initialize analyzer
    analyzer = ImprovedNgramAnalyzer(min_frequency=5)

    # Create output directory
    ngram_dir = os.path.join(RESULTS_BASE, 'ngram_results')
    os.makedirs(ngram_dir, exist_ok=True)

    # Analyze bigrams
    print("\nAnalyzing bigrams...")
    bigram_comparison = analyzer.compare_corpora(
        populist_texts,
        mainstream_texts,
        n=2,
        top_k=30
    )

    # Save bigrams
    bigram_file = os.path.join(ngram_dir, 'bigram_comparison.csv')
    with open(bigram_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Phrase', 'Type', 'Populist_Count', 'Mainstream_Count', 'Ratio'])

        for ngram, (count1, count2, ratio) in bigram_comparison['corpus1_distinctive']:
            phrase = ' '.join(ngram)
            writer.writerow([phrase, 'Populist_Distinctive', count1, count2, round(ratio, 2)])

        for ngram, (count2, count1, ratio) in bigram_comparison['corpus2_distinctive']:
            phrase = ' '.join(ngram)
            writer.writerow([phrase, 'Mainstream_Distinctive', count1, count2, round(ratio, 2)])

    print(f"✓ Saved bigrams to: {bigram_file}")

    # Analyze trigrams
    print("Analyzing trigrams...")
    trigram_comparison = analyzer.compare_corpora(
        populist_texts,
        mainstream_texts,
        n=3,
        top_k=30
    )

    # Save trigrams
    trigram_file = os.path.join(ngram_dir, 'trigram_comparison.csv')
    with open(trigram_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Phrase', 'Type', 'Populist_Count', 'Mainstream_Count', 'Ratio'])

        for ngram, (count1, count2, ratio) in trigram_comparison['corpus1_distinctive']:
            phrase = ' '.join(ngram)
            writer.writerow([phrase, 'Populist_Distinctive', count1, count2, round(ratio, 2)])

        for ngram, (count2, count1, ratio) in trigram_comparison['corpus2_distinctive']:
            phrase = ' '.join(ngram)
            writer.writerow([phrase, 'Mainstream_Distinctive', count1, count2, round(ratio, 2)])

    print(f"✓ Saved trigrams to: {trigram_file}")

    # Save summary
    summary_file = os.path.join(ngram_dir, 'ngram_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("N-GRAM ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write("TOP 10 DISTINCTIVE POPULIST BIGRAMS:\n")
        f.write("-" * 80 + "\n")
        for ngram, (count1, count2, ratio) in bigram_comparison['corpus1_distinctive'][:10]:
            phrase = ' '.join(ngram)
            f.write(f"  {phrase:25s} - {count1:3d} times ({ratio:.1f}x more than mainstream)\n")

        f.write("\n\nTOP 10 DISTINCTIVE MAINSTREAM BIGRAMS:\n")
        f.write("-" * 80 + "\n")
        for ngram, (count2, count1, ratio) in bigram_comparison['corpus2_distinctive'][:10]:
            phrase = ' '.join(ngram)
            f.write(f"  {phrase:25s} - {count2:3d} times ({ratio:.1f}x more than populist)\n")

        f.write("\n\nTOP 10 DISTINCTIVE POPULIST TRIGRAMS:\n")
        f.write("-" * 80 + "\n")
        for ngram, (count1, count2, ratio) in trigram_comparison['corpus1_distinctive'][:10]:
            phrase = ' '.join(ngram)
            f.write(f"  {phrase:35s} - {count1:3d} times ({ratio:.1f}x more)\n")

        f.write("\n\nTOP 10 DISTINCTIVE MAINSTREAM TRIGRAMS:\n")
        f.write("-" * 80 + "\n")
        for ngram, (count2, count1, ratio) in trigram_comparison['corpus2_distinctive'][:10]:
            phrase = ' '.join(ngram)
            f.write(f"  {phrase:35s} - {count2:3d} times ({ratio:.1f}x more)\n")

    print(f"✓ Summary saved to: {summary_file}")


def run_statistical_tests(results):
    """
    PART 3: Statistical tests
    """
    print("\n\n" + "=" * 80)
    print("PART 3: STATISTICAL TESTS")
    print("=" * 80)
    print()

    import pandas as pd

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Check categories
    categories = df['category'].value_counts()
    print("Speech counts by category:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    print()

    # Define features to test
    features_to_test = [
        'vader_compound',
        'vader_positive',
        'vader_negative',
        'anti_elite_density',
        'crisis_density',
        'certainty_density',
        'hedging_density',
        'certainty_hedging_ratio',
        'we_density',
        'they_density',
        'we_they_ratio',
        'flesch_reading_ease',
        'avg_sentence_length',
        'difficult_words_pct',
    ]

    # Initialize tester
    tester = StatisticalTester(alpha=0.05)

    # Run tests
    print("Running t-tests on all features...\n")

    test_results = []
    for feature in features_to_test:
        group1_data = df[df['category'] == 'Populist'][feature].dropna()
        group2_data = df[df['category'] == 'Mainstream'][feature].dropna()

        result = tester.independent_t_test(group1_data, group2_data, feature)
        test_results.append(result)

    # Convert to DataFrame and sort by p-value
    results_df = pd.DataFrame(test_results)
    results_df = results_df.sort_values('p_value')

    # Print summary table
    print("\n" + "=" * 100)
    print(f"{'Feature':<30} {'Populist':>12} {'Mainstream':>12} {'Diff':>10} {'p-value':>10} {'d':>8} {'Sig':>6}")
    print("-" * 100)

    for _, row in results_df.iterrows():
        sig_marker = "***" if row['p_value'] < 0.001 else "**" if row['p_value'] < 0.01 else "*" if row['p_value'] < 0.05 else ""

        print(f"{row['feature']:<30} {row['group1_mean']:>12.2f} {row['group2_mean']:>12.2f} "
              f"{row['mean_difference']:>10.2f} {row['p_value']:>10.4f} {row['cohens_d']:>8.2f} {sig_marker:>6}")

    print("-" * 100)
    print("Significance: *** p<0.001, ** p<0.01, * p<0.05")
    print("=" * 100)

    # Save results
    output_file = os.path.join(RESULTS_BASE, 'statistical_tests.csv')
    results_df.to_csv(output_file, index=False)
    print(f"\n✓ Statistical results saved to: {output_file}")

    return results_df


def generate_master_report(feature_results, stat_results):
    """
    PART 4: Generate master summary report
    """
    print("\n\n" + "=" * 80)
    print("PART 4: GENERATING MASTER REPORT")
    print("=" * 80)
    print()

    report_file = os.path.join(RESULTS_BASE, 'MASTER_ANALYSIS_REPORT.txt')

    with open(report_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("COMPLETE CORPUS ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Corpus Size: {len(feature_results)} speeches\n")
        f.write(f"Corpus Location: {CORPUS_DIR}\n\n")

        # Count by category
        import pandas as pd
        df = pd.DataFrame(feature_results)
        categories = df['category'].value_counts()

        f.write("CORPUS COMPOSITION:\n")
        f.write("-" * 80 + "\n")
        for cat, count in categories.items():
            f.write(f"  {cat}: {count} speeches\n")
        f.write("\n\n")

        # Significant findings
        f.write("SIGNIFICANT FINDINGS (p < 0.05):\n")
        f.write("=" * 80 + "\n\n")

        significant = stat_results[stat_results['is_significant']]

        if len(significant) == 0:
            f.write("No significant differences found.\n")
        else:
            for idx, row in significant.iterrows():
                direction = "higher" if row['mean_difference'] > 0 else "lower"

                f.write(f"{row['feature'].upper().replace('_', ' ')}:\n")
                f.write(f"  Populist:    M = {row['group1_mean']:.2f}, SD = {row['group1_std']:.2f}\n")
                f.write(f"  Mainstream:  M = {row['group2_mean']:.2f}, SD = {row['group2_std']:.2f}\n")
                f.write(f"  Difference:  {row['mean_difference']:+.2f} (Populist {direction})\n")
                f.write(f"  Statistics:  t({int(row['group1_n'] + row['group2_n'] - 2)}) = {row['t_statistic']:.2f}, ")
                f.write(f"p = {row['p_value']:.4f}, d = {row['cohens_d']:.2f}\n")
                f.write(f"  Effect size: {row['effect_size']}\n\n")

        f.write("\n")
        f.write("NON-SIGNIFICANT FINDINGS (p ≥ 0.05):\n")
        f.write("=" * 80 + "\n\n")

        non_significant = stat_results[~stat_results['is_significant']]

        for idx, row in non_significant.iterrows():
            f.write(f"{row['feature'].replace('_', ' ')}: p = {row['p_value']:.4f}\n")

        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write("FILES GENERATED:\n")
        f.write("=" * 80 + "\n\n")
        f.write("1. all_features_combined.csv - All linguistic features for all speeches\n")
        f.write("2. ngram_results/bigram_comparison.csv - Distinctive 2-word phrases\n")
        f.write("3. ngram_results/trigram_comparison.csv - Distinctive 3-word phrases\n")
        f.write("4. ngram_results/ngram_summary.txt - N-gram analysis summary\n")
        f.write("5. statistical_tests.csv - Complete statistical test results\n")
        f.write("6. MASTER_ANALYSIS_REPORT.txt - This file\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("ANALYSIS COMPLETE\n")
        f.write("=" * 80 + "\n")

    print(f"✓ Master report saved to: {report_file}")


def main():
    """
    Main execution: Run complete analysis pipeline
    """

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COMPLETE CORPUS ANALYSIS" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    print("This script will run:")
    print("  1. All 7 linguistic features (VADER sentiment, anti-elite, crisis, certainty,")
    print("     pronouns, readability)")
    print("  2. N-gram analysis (bigrams and trigrams)")
    print("  3. Statistical tests (t-tests, effect sizes)")
    print("  4. Generate master report")
    print("\n")

    # Create results directory
    os.makedirs(RESULTS_BASE, exist_ok=True)

    # Part 1: Linguistic features
    feature_results = run_linguistic_features()

    if feature_results is None:
        print("\n❌ Analysis failed - check paths and try again")
        return

    # Part 2: N-grams
    run_ngram_analysis()

    # Part 3: Statistical tests
    stat_results = run_statistical_tests(feature_results)

    # Part 4: Master report
    generate_master_report(feature_results, stat_results)

    print("\n\n" + "=" * 80)
    print("✓ ✓ ✓ COMPLETE ANALYSIS FINISHED ✓ ✓ ✓")
    print("=" * 80)
    print(f"\nAll results saved to: {RESULTS_BASE}/")
    print("\nGenerated files:")
    print("  • all_features_combined.csv")
    print("  • statistical_tests.csv")
    print("  • ngram_results/bigram_comparison.csv")
    print("  • ngram_results/trigram_comparison.csv")
    print("  • ngram_results/ngram_summary.txt")
    print("  • MASTER_ANALYSIS_REPORT.txt")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
