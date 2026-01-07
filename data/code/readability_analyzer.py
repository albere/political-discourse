"""
Readability Analysis using textstat library
More accurate than custom implementation due to CMU dictionary for syllables

Install: pip install textstat
Also needs: python -m nltk.downloader cmudict punkt
"""

import textstat

class ReadabilityAnalyzer:
    """
    Analyze readability using textstat library
    Provides access to all major readability formulas
    """
    
    def __init__(self):
        # Set language to English
        textstat.set_lang('en')
    
    def analyze(self, text):
        """
        Complete readability analysis using textstat
        """
        
        # === PRIMARY READABILITY SCORES ===
        
        # Flesch Reading Ease (0-100, higher = easier)
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        
        # SMOG Index
        smog_index = textstat.smog_index(text)
        
        # Coleman-Liau Index
        coleman_liau = textstat.coleman_liau_index(text)
        
        # Automated Readability Index
        ari = textstat.automated_readability_index(text)
        
        # Dale-Chall Readability Score
        dale_chall = textstat.dale_chall_readability_score(text)
        
        # Gunning Fog Index
        gunning_fog = textstat.gunning_fog(text)
        
        # Linsear Write Formula
        linsear_write = textstat.linsear_write_formula(text)
        
        # === CONSENSUS SCORE ===
        # Textstat's aggregate estimate (returns string like "7th and 8th grade")
        # We can also get it as a float
        try:
            text_standard = textstat.text_standard(text, float_output=True)
        except:
            # Fallback if float_output not supported
            text_standard = flesch_kincaid_grade
        
        # === TEXT STATISTICS ===
        word_count = textstat.lexicon_count(text, removepunct=True)
        sentence_count = textstat.sentence_count(text)
        syllable_count = textstat.syllable_count(text)
        char_count = textstat.char_count(text, ignore_spaces=True)
        
        # Difficult words (not in Dale-Chall easy word list)
        difficult_words = textstat.difficult_words(text)
        
        # Polysyllabic words (3+ syllables)
        polysyllabic_count = textstat.polysyllabcount(text)
        
        # Monosyllabic words
        monosyllabic_count = textstat.monosyllabcount(text)
        
        # === DERIVED METRICS ===
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        avg_syllables_per_word = syllable_count / word_count if word_count > 0 else 0
        avg_chars_per_word = char_count / word_count if word_count > 0 else 0
        difficult_words_pct = (difficult_words / word_count * 100) if word_count > 0 else 0
        polysyllabic_pct = (polysyllabic_count / word_count * 100) if word_count > 0 else 0
        
        return {
            # Readability scores
            'flesch_reading_ease': flesch_reading_ease,
            'flesch_kincaid_grade': flesch_kincaid_grade,
            'smog_index': smog_index,
            'coleman_liau_index': coleman_liau,
            'automated_readability_index': ari,
            'dale_chall_score': dale_chall,
            'gunning_fog': gunning_fog,
            'linsear_write': linsear_write,
            'consensus_grade_level': text_standard,
            
            # Basic statistics
            'word_count': word_count,
            'sentence_count': sentence_count,
            'syllable_count': syllable_count,
            'char_count': char_count,
            'difficult_words': difficult_words,
            'polysyllabic_count': polysyllabic_count,
            'monosyllabic_count': monosyllabic_count,
            
            # Derived metrics
            'avg_sentence_length': avg_sentence_length,
            'avg_syllables_per_word': avg_syllables_per_word,
            'avg_chars_per_word': avg_chars_per_word,
            'difficult_words_pct': difficult_words_pct,
            'polysyllabic_pct': polysyllabic_pct,
        }
    
    def interpret_flesch(self, score):
        """Interpret Flesch Reading Ease score"""
        if score >= 90:
            return "Very Easy (5th grade)"
        elif score >= 80:
            return "Easy (6th grade)"
        elif score >= 70:
            return "Fairly Easy (7th grade)"
        elif score >= 60:
            return "Standard (8th-9th grade)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif score >= 30:
            return "Difficult (College)"
        else:
            return "Very Difficult (Graduate)"
    
    def get_complexity_level(self, grade_level):
        """Simple complexity classification (1-5 scale)"""
        if grade_level < 6:
            return 1, "Elementary"
        elif grade_level < 9:
            return 2, "Middle School"
        elif grade_level < 13:
            return 3, "High School"
        elif grade_level < 16:
            return 4, "College"
        else:
            return 5, "Graduate"


def create_readability_summary(results):
    """Create human-readable summary"""
    analyzer = ReadabilityAnalyzer()
    flesch_interp = analyzer.interpret_flesch(results['flesch_reading_ease'])
    complexity_num, complexity_name = analyzer.get_complexity_level(results['consensus_grade_level'])
    
    summary = f"""
READABILITY ANALYSIS SUMMARY (using textstat + NLTK)
{'=' * 70}

PRIMARY METRICS:
  Flesch Reading Ease:      {results['flesch_reading_ease']:6.1f}  ({flesch_interp})
  Flesch-Kincaid Grade:     {results['flesch_kincaid_grade']:6.1f}  (US grade level)
  Consensus Grade Level:    {results['consensus_grade_level']:6.1f}
  
ADDITIONAL METRICS:
  SMOG Index:               {results['smog_index']:6.1f}
  Coleman-Liau Index:       {results['coleman_liau_index']:6.1f}
  Gunning Fog:              {results['gunning_fog']:6.1f}
  Automated Readability:    {results['automated_readability_index']:6.1f}
  Dale-Chall Score:         {results['dale_chall_score']:6.1f}
  Linsear Write:            {results['linsear_write']:6.1f}

TEXT STATISTICS:
  Word count:               {results['word_count']:6d}
  Sentence count:           {results['sentence_count']:6d}
  Avg sentence length:      {results['avg_sentence_length']:6.1f} words
  Avg syllables per word:   {results['avg_syllables_per_word']:6.2f}
  Avg characters per word:  {results['avg_chars_per_word']:6.1f}
  
WORD COMPLEXITY:
  Difficult words:          {results['difficult_words']:6d} ({results['difficult_words_pct']:.1f}%)
  Polysyllabic words:       {results['polysyllabic_count']:6d} ({results['polysyllabic_pct']:.1f}%)
  Monosyllabic words:       {results['monosyllabic_count']:6d}

INTERPRETATION:
  Complexity Level:         {complexity_num}/5 ({complexity_name})
  Reading Level:            {flesch_interp.split('(')[1].replace(')', '')}

{'=' * 70}
    """
    return summary


# Example usage and testing
if __name__ == "__main__":
    
    # First, make sure NLTK data is downloaded
    print("Checking NLTK data...")
    try:
        import nltk
        nltk.download('cmudict', quiet=True)
        nltk.download('punkt', quiet=True)
        print("✓ NLTK data ready\n")
    except:
        print("⚠ NLTK download failed - syllable counts may be less accurate\n")
    
    analyzer = ReadabilityAnalyzer()
    
    # Test texts
    simple_text = """
    We need change. They failed us. We will win. Our country is great.
    You deserve better. I will fight for you. We are strong. They are weak.
    Together we win. This is our time. We will succeed. Trust me on this.
    The people are ready. We know what to do. They do not care. We care deeply.
    """
    
    complex_text = """
    The contemporary geopolitical landscape necessitates a comprehensive
    reevaluation of our multilateral institutional frameworks. The
    epistemological foundations of our policy implementations require
    substantial recalibration to adequately address the multifaceted
    challenges inherent in our increasingly interconnected global economy.
    Furthermore, the ramifications of our strategic deliberations must be
    assessed through a sophisticated analytical lens that incorporates
    both quantitative metrics and qualitative considerations. The
    implementation of these methodologies demands unprecedented coordination.
    """
    
    print("=" * 70)
    print("TESTING READABILITY ANALYZER (TEXTSTAT VERSION)")
    print("=" * 70)
    
    # Analyze simple text
    print("\nSIMPLE (POPULIST-STYLE) TEXT:")
    simple_results = analyzer.analyze(simple_text)
    print(create_readability_summary(simple_results))
    
    # Analyze complex text
    print("\nCOMPLEX (ACADEMIC-STYLE) TEXT:")
    complex_results = analyzer.analyze(complex_text)
    print(create_readability_summary(complex_results))
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON:")
    print("=" * 70)
    print(f"\nFlesch Reading Ease:")
    print(f"  Simple:  {simple_results['flesch_reading_ease']:5.1f}  ({analyzer.interpret_flesch(simple_results['flesch_reading_ease'])})")
    print(f"  Complex: {complex_results['flesch_reading_ease']:5.1f}  ({analyzer.interpret_flesch(complex_results['flesch_reading_ease'])})")
    
    print(f"\nGrade Level:")
    print(f"  Simple:  {simple_results['flesch_kincaid_grade']:5.1f}")
    print(f"  Complex: {complex_results['flesch_kincaid_grade']:5.1f}")
    print(f"  Difference: {complex_results['flesch_kincaid_grade'] - simple_results['flesch_kincaid_grade']:+5.1f} grades")
    
    print(f"\nAverage Sentence Length:")
    print(f"  Simple:  {simple_results['avg_sentence_length']:5.1f} words")
    print(f"  Complex: {complex_results['avg_sentence_length']:5.1f} words")
    
    print(f"\nDifficult Words:")
    print(f"  Simple:  {simple_results['difficult_words_pct']:5.1f}%")
    print(f"  Complex: {complex_results['difficult_words_pct']:5.1f}%")
    
    print("\n" + "=" * 70)
    print("✓ Tests complete!")
    print("\nNOTE: This version uses textstat + NLTK for accurate syllable counting")
