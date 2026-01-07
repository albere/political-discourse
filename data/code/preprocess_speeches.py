#!/usr/bin/env python3
"""
Political Speech Preprocessing Pipeline
Week 3 - compling Project
Author: Albere
Purpose: Clean and preprocess 28 political speeches for linguistic analysis
"""

import spacy
import pandas as pd
import re
from pathlib import Path
import unicodedata

# Load spaCy English model
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")

def fix_encoding(text):
    """
    Fix common encoding issues in speech transcripts.
    Handles smart quotes, apostrophes, dashes, etc.
    """
    # Common encoding fixes
    replacements = {
        'â€™': "'",  # Smart apostrophe
        'â€˜': "'",  # Opening smart quote
        'â€œ': '"',  # Opening smart double quote
        'â€': '"',   # Closing smart double quote
        'â€"': '—',  # Em dash
        'â€"': '–',  # En dash
        'â€¦': '...',  # Ellipsis
        '\u2019': "'",  # Unicode apostrophe
        '\u2018': "'",  # Unicode quote
        '\u201c': '"',  # Unicode quote
        '\u201d': '"',  # Unicode quote
        '\u2013': '-',  # En dash
        '\u2014': '—',  # Em dash
        '\xa0': ' ',    # Non-breaking space
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)

    return text


def clean_text(text):
    """
    Clean speech text while preserving structure and meaning.
    - Fix encoding issues
    - Remove excessive whitespace
    - Normalize punctuation
    - Keep paragraph structure
    """
    # Fix encoding problems
    text = fix_encoding(text)

    # Remove any HTML/XML tags if present
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize whitespace but preserve paragraph breaks
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    # Preserve paragraph breaks (double newlines)
    # But clean up excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)

    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def preprocess_speech(text, remove_stopwords=False):
    """
    Process speech with spaCy pipeline.

    Args:
        text (str): Raw speech text
        remove_stopwords (bool): Whether to remove stopwords

    Returns:
        dict: Dictionary with processed text and metadata
    """
    # Clean the text first
    cleaned_text = clean_text(text)

    # Process with spaCy
    doc = nlp(cleaned_text)

    # Extract tokens with linguistic features
    tokens_data = []
    for token in doc:
        token_info = {
            'text': token.text,
            'lemma': token.lemma_,
            'pos': token.pos_,
            'tag': token.tag_,
            'is_stop': token.is_stop,
            'is_punct': token.is_punct,
            'is_alpha': token.is_alpha,
        }
        tokens_data.append(token_info)

    # Create cleaned token list (no punctuation, optionally no stopwords)
    if remove_stopwords:
        clean_tokens = [token.lemma_.lower() for token in doc
                       if not token.is_stop and not token.is_punct and token.is_alpha]
    else:
        clean_tokens = [token.lemma_.lower() for token in doc
                       if not token.is_punct and token.is_alpha]

    # Extract sentences
    sentences = [sent.text.strip() for sent in doc.sents]

    # Calculate basic statistics
    stats = {
        'total_tokens': len(doc),
        'unique_tokens': len(set([token.text.lower() for token in doc if token.is_alpha])),
        'sentences': len(sentences),
        'avg_sentence_length': len(doc) / len(sentences) if sentences else 0,
        'stopwords': sum(1 for token in doc if token.is_stop),
        'nouns': sum(1 for token in doc if token.pos_ == 'NOUN'),
        'verbs': sum(1 for token in doc if token.pos_ == 'VERB'),
        'adjectives': sum(1 for token in doc if token.pos_ == 'ADJ'),
    }

    return {
        'cleaned_text': cleaned_text,
        'tokens': tokens_data,
        'clean_tokens': clean_tokens,
        'sentences': sentences,
        'stats': stats,
        'spacy_doc': doc  # Keep doc for further analysis
    }


def process_speech_file(filepath, output_dir=None):
    """
    Process a single speech file.

    Args:
        filepath (str or Path): Path to the speech text file
        output_dir (str or Path, optional): Directory to save processed output

    Returns:
        dict: Processed speech data
    """
    filepath = Path(filepath)

    print(f"\nProcessing: {filepath.name}")

    # Read the file
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()

    # Preprocess
    processed = preprocess_speech(raw_text)

    # Print some stats
    print(f"  Original length: {len(raw_text)} characters")
    print(f"  Cleaned length: {len(processed['cleaned_text'])} characters")
    print(f"  Tokens: {processed['stats']['total_tokens']}")
    print(f"  Sentences: {processed['stats']['sentences']}")
    print(f"  Unique words: {processed['stats']['unique_tokens']}")

    # Save processed version if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save cleaned text
        output_file = output_dir / f"{filepath.stem}_cleaned.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed['cleaned_text'])

        print(f"  Saved cleaned text to: {output_file}")

    return processed


def process_corpus(input_dir, metadata_file, output_dir):
    """
    Process entire corpus of speeches.

    Args:
        input_dir (str): Directory containing raw speech files
        metadata_file (str): Path to metadata CSV
        output_dir (str): Directory to save processed outputs
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load metadata
    print(f"Loading metadata from: {metadata_file}")
    metadata = pd.read_csv(metadata_file)

    print(f"\nFound {len(metadata)} speeches in metadata")
    print(f"Looking for files in: {input_dir}")

    # Process each speech
    results = []

    for idx, row in metadata.iterrows():
        filename = row['Filename']
        filepath = input_dir / filename

        if not filepath.exists():
            print(f"\n❌ WARNING: File not found: {filepath}")
            continue

        try:
            # Process the speech
            processed = process_speech_file(filepath, output_dir)

            # Add metadata to results
            result = {
                'Text_ID': row['Text_ID'],
                'Country': row['Country'],
                'Category': row['Category'],
                'Speaker': row['Speaker'],
                'Date': row['Date'],
                'Filename': filename,
                **processed['stats']
            }
            results.append(result)

        except Exception as e:
            print(f"\n❌ ERROR processing {filename}: {e}")
            continue

    # Save processing results
    results_df = pd.DataFrame(results)
    results_file = output_dir / 'preprocessing_stats.csv'
    results_df.to_csv(results_file, index=False)

    print(f"\n✅ Processing complete!")
    print(f"   Processed: {len(results)} / {len(metadata)} speeches")
    print(f"   Stats saved to: {results_file}")

    return results_df


def main():
    """
    Main function - customize paths here for your setup.
    """
    # CUSTOMIZE THESE PATHS FOR YOUR LOCAL MACHINE
    INPUT_DIR = "/home/albere/compling/data/raw"  # Where your raw speeches are
    METADATA_FILE = "/home/albere/compling/data/docs/metadata.csv"  # Your metadata CSV
    OUTPUT_DIR = "/home/albere/compling/data/processed"  # Where to save processed files

    print("="*60)
    print("Political Speech Preprocessing Pipeline")
    print("="*60)

    # Process the entire corpus
    stats = process_corpus(INPUT_DIR, METADATA_FILE, OUTPUT_DIR)

    print("\n" + "="*60)
    print("Summary Statistics:")
    print("="*60)
    print(stats[['Text_ID', 'Speaker', 'total_tokens', 'sentences', 'unique_tokens']].to_string())


if __name__ == "__main__":
    main()
