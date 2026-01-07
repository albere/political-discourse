"""
Anti-Elite Rhetoric Detector
Identifies and quantifies anti-establishment language in political speeches
"""

from collections import Counter
import re

class AntiEliteDetector:
    """
    Detects anti-elite rhetoric patterns in political speeches
    
    Categories:
    1. Elite/establishment references (negative)
    2. System criticism (negative)
    3. Populist positive framing (positive)
    4. Corruption/betrayal language (strong negative)
    """
    
    def __init__(self):
        # Anti-elite terms (UK and USA specific)
        self.anti_elite_terms = {
            # General establishment
            'establishment': -2.0,
            'elite': -2.5,
            'elites': -2.5,
            'ruling class': -2.5,
            'political class': -2.0,
            'political elite': -2.5,
            
            # UK-specific
            'westminster': -1.5,
            'westminster bubble': -2.0,
            'brussels': -2.0,
            'brussels bureaucrats': -2.5,
            'eurocrats': -2.0,
            
            # USA-specific
            'washington': -1.5,
            'washington insiders': -2.0,
            'beltway': -1.5,
            'deep state': -2.5,
            
            # Career politicians
            'career politicians': -2.0,
            'career politician': -2.0,
            'professional politicians': -2.0,
            
            # Out of touch framing
            'out of touch': -2.0,
            'disconnected': -1.5,
            'ivory tower': -2.0,
        }
        
        # System criticism
        self.system_criticism = {
            'rigged': -2.5,
            'rigged system': -3.0,
            'corrupt': -3.0,
            'corrupted': -2.5,
            'corruption': -2.5,
            'swamp': -2.0,
            'drain the swamp': -2.0,
            'broken system': -2.5,
            'broken': -1.5,
            'failed': -2.0,
            'failing': -1.5,
            'betrayed': -3.0,
            'betrayal': -2.5,
            'sold out': -2.5,
            'crooked': -2.5,
        }
        
        # Populist positive frames (us vs them positive)
        self.populist_positive = {
            'ordinary people': 2.0,
            'ordinary': 1.0,
            'working people': 1.5,
            'working families': 1.5,
            'hardworking families': 2.0,
            'hardworking': 1.5,
            'the people': 1.5,
            'take back control': 2.5,
            'take control': 2.0,
            'sovereignty': 2.0,
            'our country back': 2.0,
            'common sense': 1.5,
            'real people': 1.5,
        }
        
        # Negative frames for "the people"
        self.people_negative = {
            'forgotten': -2.0,
            'forgotten people': -2.5,
            'left behind': -2.0,
            'ignored': -1.5,
            'neglected': -1.5,
        }
        
        # Compile all terms for quick lookup
        self.all_terms = {
            **self.anti_elite_terms,
            **self.system_criticism,
            **self.populist_positive,
            **self.people_negative
        }
    
    def count_terms(self, text, term_dict):
        """
        Count occurrences of terms in text
        Returns counts and weighted score
        """
        text_lower = text.lower()
        
        term_counts = {}
        total_count = 0
        total_score = 0.0
        
        # Sort by length (longest first) to catch multi-word phrases
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        
        for term in sorted_terms:
            count = text_lower.count(term)
            if count > 0:
                term_counts[term] = count
                total_count += count
                total_score += (term_dict[term] * count)
        
        return {
            'count': total_count,
            'score': total_score,
            'terms_found': term_counts
        }
    
    def analyze(self, text):
        """
        Full anti-elite rhetoric analysis
        
        Returns:
            dict with counts, scores, and density metrics
        """
        word_count = len(text.split())
        
        # Analyze each category
        anti_elite = self.count_terms(text, self.anti_elite_terms)
        system_crit = self.count_terms(text, self.system_criticism)
        pop_positive = self.count_terms(text, self.populist_positive)
        people_neg = self.count_terms(text, self.people_negative)
        
        # Combined anti-elite score (negative terms)
        anti_elite_total_count = anti_elite['count'] + system_crit['count'] + people_neg['count']
        anti_elite_total_score = anti_elite['score'] + system_crit['score'] + people_neg['score']
        
        # Net populist score (includes positive framing)
        net_score = anti_elite_total_score + pop_positive['score']
        
        return {
            # Anti-elite metrics
            'anti_elite_count': anti_elite['count'],
            'anti_elite_score': anti_elite['score'],
            'anti_elite_terms': anti_elite['terms_found'],
            
            # System criticism
            'system_criticism_count': system_crit['count'],
            'system_criticism_score': system_crit['score'],
            'system_criticism_terms': system_crit['terms_found'],
            
            # Populist positive
            'populist_positive_count': pop_positive['count'],
            'populist_positive_score': pop_positive['score'],
            'populist_positive_terms': pop_positive['terms_found'],
            
            # People negative framing
            'people_negative_count': people_neg['count'],
            'people_negative_score': people_neg['score'],
            'people_negative_terms': people_neg['terms_found'],
            
            # Combined metrics
            'total_anti_elite_count': anti_elite_total_count,
            'total_anti_elite_score': anti_elite_total_score,
            'net_populist_score': net_score,
            
            # Density (per 1000 words)
            'anti_elite_density': (anti_elite_total_count / word_count * 1000) if word_count > 0 else 0,
            'word_count': word_count,
        }
    
    def compare_speeches(self, text1, text2, label1="Speech 1", label2="Speech 2"):
        """
        Compare anti-elite rhetoric between two speeches
        """
        results1 = self.analyze(text1)
        results2 = self.analyze(text2)
        
        print(f"\n{'=' * 60}")
        print(f"ANTI-ELITE RHETORIC COMPARISON")
        print(f"{'=' * 60}\n")
        
        print(f"{label1}:")
        print(f"  Anti-elite terms: {results1['total_anti_elite_count']}")
        print(f"  Density: {results1['anti_elite_density']:.2f} per 1000 words")
        print(f"  Score: {results1['total_anti_elite_score']:.2f}")
        
        print(f"\n{label2}:")
        print(f"  Anti-elite terms: {results2['total_anti_elite_count']}")
        print(f"  Density: {results2['anti_elite_density']:.2f} per 1000 words")
        print(f"  Score: {results2['total_anti_elite_score']:.2f}")
        
        print(f"\nDifference:")
        density_diff = results1['anti_elite_density'] - results2['anti_elite_density']
        print(f"  Density difference: {density_diff:+.2f} per 1000 words")
        
        return results1, results2


def create_custom_vader_lexicon():
    """
    Create a dictionary for extending VADER's lexicon
    Returns dict that can be added to VADER
    """
    detector = AntiEliteDetector()
    
    # Flatten all terms into single dictionary for VADER
    custom_lexicon = {}
    custom_lexicon.update(detector.anti_elite_terms)
    custom_lexicon.update(detector.system_criticism)
    custom_lexicon.update(detector.populist_positive)
    custom_lexicon.update(detector.people_negative)
    
    return custom_lexicon


# Example usage and testing
if __name__ == "__main__":
    
    detector = AntiEliteDetector()
    
    # Test speeches
    populist_text = """
    The political establishment has failed you. The elites in Westminster
    and Brussels have rigged the system against ordinary working people.
    They are out of touch with real families. We must take back control
    and drain the swamp. The forgotten people deserve better. Career
    politicians have betrayed us for too long.
    """
    
    mainstream_text = """
    Our government is delivering strong economic growth and stability.
    We have implemented responsible fiscal policies that benefit all
    citizens. Through careful management and sound leadership, we are
    creating opportunities for families across the nation. We remain
    committed to prosperity and security for all.
    """
    
    # Analyze
    print("\n" + "=" * 60)
    print("TESTING ANTI-ELITE DETECTOR")
    print("=" * 60)
    
    pop_results = detector.analyze(populist_text)
    main_results = detector.analyze(mainstream_text)
    
    print("\nPOPULIST SPEECH:")
    print(f"  Anti-elite count: {pop_results['total_anti_elite_count']}")
    print(f"  Anti-elite density: {pop_results['anti_elite_density']:.2f} per 1000 words")
    print(f"  Terms found: {list(pop_results['anti_elite_terms'].keys())}")
    print(f"  System criticism: {list(pop_results['system_criticism_terms'].keys())}")
    
    print("\nMAINSTREAM SPEECH:")
    print(f"  Anti-elite count: {main_results['total_anti_elite_count']}")
    print(f"  Anti-elite density: {main_results['anti_elite_density']:.2f} per 1000 words")
    
    print("\n" + "=" * 60)
    print(f"Populist speech has {pop_results['anti_elite_density'] / max(main_results['anti_elite_density'], 0.1):.1f}x more anti-elite rhetoric")
    print("=" * 60)
    
    # Test custom VADER integration
    print("\n" + "=" * 60)
    print("TESTING VADER INTEGRATION")
    print("=" * 60)
    
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        # Standard VADER
        standard = SentimentIntensityAnalyzer()
        
        # Custom VADER
        custom = SentimentIntensityAnalyzer()
        custom_lex = create_custom_vader_lexicon()
        custom.lexicon.update(custom_lex)
        
        test_text = "The establishment elites have rigged the system against ordinary people"
        
        print(f"\nTest text: '{test_text}'")
        print(f"\nStandard VADER: {standard.polarity_scores(test_text)['compound']:.3f}")
        print(f"Custom VADER: {custom.polarity_scores(test_text)['compound']:.3f}")
        print(f"Difference: {custom.polarity_scores(test_text)['compound'] - standard.polarity_scores(test_text)['compound']:.3f}")
        
    except ImportError:
        print("\nVADER not installed - skipping integration test")
    
    print("\n✓ Tests complete!")
