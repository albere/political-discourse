"""
Certainty Markers Detector
Identifies expressions of certainty, confidence, and epistemic stance in political speeches

Populists often use high-certainty language to project confidence and authority,
while hedging language (uncertainty) may be less common.
"""

from collections import Counter
import re

class CertaintyDetector:
    """
    Detects certainty markers and hedging language in political speeches
    
    Categories:
    1. High certainty markers (absolute, definite statements)
    2. Modal verbs of certainty (will, must, shall)
    3. Emphatic certainty (clearly, obviously, definitely)
    4. Hedging language (uncertainty markers)
    5. Modal verbs of possibility (might, could, may)
    """
    
    def __init__(self):
        # High certainty markers (absolute statements)
        self.certainty_markers = {
            'certain': 3.0,
            'certainly': 3.0,
            'sure': 2.5,
            'surely': 2.5,
            'definite': 3.0,
            'definitely': 3.0,
            'absolute': 3.5,
            'absolutely': 3.5,
            'undoubtedly': 3.5,
            'without doubt': 3.5,
            'no doubt': 3.0,
            'beyond doubt': 3.5,
            'unquestionably': 3.5,
            'indisputable': 3.5,
            'indisputably': 3.5,
            'inevitable': 3.0,
            'inevitably': 3.0,
            'guaranteed': 3.0,
            'guarantee': 2.5,
        }
        
        # Modal verbs of high certainty
        self.certainty_modals = {
            'will': 2.0,
            'shall': 2.5,
            'must': 2.5,
            'have to': 2.0,
            'need to': 2.0,
            'going to': 1.5,
        }
        
        # Emphatic certainty (adverbs that emphasize certainty)
        self.emphatic_certainty = {
            'clearly': 2.5,
            'obviously': 3.0,
            'evidently': 2.5,
            'plainly': 2.5,
            'manifestly': 3.0,
            'patently': 3.0,
            'undeniably': 3.5,
            'incontrovertibly': 3.5,
            'unequivocally': 3.5,
            'categorically': 3.0,
            'absolutely certain': 4.0,
            'perfectly clear': 3.5,
            'crystal clear': 3.5,
            'without question': 3.5,
        }
        
        # Hedging language (uncertainty markers)
        self.hedging_markers = {
            'maybe': -2.0,
            'perhaps': -2.0,
            'possibly': -2.0,
            'probably': -1.5,
            'likely': -1.0,
            'unlikely': -1.0,
            'might': -2.0,
            'could': -1.5,
            'may': -1.5,
            'can': -1.0,  # Less hedging than might/could
            'seem': -1.5,
            'seems': -1.5,
            'appear': -1.5,
            'appears': -1.5,
            'suggest': -1.5,
            'suggests': -1.5,
            'indicate': -1.0,
            'indicates': -1.0,
            'tend to': -1.5,
            'tends to': -1.5,
            'somewhat': -1.5,
            'rather': -1.0,
            'fairly': -1.0,
            'quite': -1.0,
            'relatively': -1.5,
            'arguably': -2.0,
            'conceivably': -2.0,
            'potentially': -1.5,
            'presumably': -1.5,
            'supposedly': -2.0,
            'allegedly': -2.5,
        }
        
        # Additional certainty phrases
        self.certainty_phrases = {
            'make no mistake': 3.5,
            'let me be clear': 3.0,
            'the fact is': 3.0,
            'the truth is': 3.0,
            'there is no question': 3.5,
            'rest assured': 3.0,
            'mark my words': 3.5,
            'you can be sure': 3.0,
            'i guarantee': 3.5,
            'i promise': 3.0,
            'we will': 2.5,
            'we must': 2.5,
            'we shall': 3.0,
        }
        
        # Combine all certainty markers (positive scores)
        self.all_certainty = {
            **self.certainty_markers,
            **self.certainty_modals,
            **self.emphatic_certainty,
            **self.certainty_phrases
        }
        
        # All terms including hedging (negative scores)
        self.all_terms = {
            **self.all_certainty,
            **self.hedging_markers
        }
    
    def count_terms(self, text, term_dict):
        """Count occurrences of terms in text"""
        text_lower = text.lower()
        
        term_counts = {}
        total_count = 0
        total_score = 0.0
        
        # Sort by length (longest first) to catch multi-word phrases
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        
        for term in sorted_terms:
            # Use word boundaries for short words to avoid false matches
            if len(term.split()) == 1 and len(term) <= 4:
                # Word boundary matching for short terms
                pattern = r'\b' + re.escape(term) + r'\b'
                count = len(re.findall(pattern, text_lower))
            else:
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
        Full certainty analysis
        
        Returns:
            dict with counts, scores, and metrics for certainty vs hedging
        """
        word_count = len(text.split())
        
        # Analyze certainty (positive scores)
        certainty_basic = self.count_terms(text, self.certainty_markers)
        certainty_modals = self.count_terms(text, self.certainty_modals)
        certainty_emphatic = self.count_terms(text, self.emphatic_certainty)
        certainty_phrases = self.count_terms(text, self.certainty_phrases)
        
        # Analyze hedging (negative scores)
        hedging = self.count_terms(text, self.hedging_markers)
        
        # Combined metrics
        total_certainty_count = (certainty_basic['count'] + certainty_modals['count'] + 
                                certainty_emphatic['count'] + certainty_phrases['count'])
        total_certainty_score = (certainty_basic['score'] + certainty_modals['score'] + 
                                certainty_emphatic['score'] + certainty_phrases['score'])
        
        # Net certainty (certainty minus hedging)
        net_certainty_score = total_certainty_score + hedging['score']  # hedging has negative scores
        
        return {
            # Certainty markers
            'certainty_basic_count': certainty_basic['count'],
            'certainty_basic_score': certainty_basic['score'],
            'certainty_basic_terms': certainty_basic['terms_found'],
            
            # Modal certainty
            'certainty_modal_count': certainty_modals['count'],
            'certainty_modal_score': certainty_modals['score'],
            'certainty_modal_terms': certainty_modals['terms_found'],
            
            # Emphatic certainty
            'certainty_emphatic_count': certainty_emphatic['count'],
            'certainty_emphatic_score': certainty_emphatic['score'],
            'certainty_emphatic_terms': certainty_emphatic['terms_found'],
            
            # Certainty phrases
            'certainty_phrase_count': certainty_phrases['count'],
            'certainty_phrase_score': certainty_phrases['score'],
            'certainty_phrase_terms': certainty_phrases['terms_found'],
            
            # Hedging
            'hedging_count': hedging['count'],
            'hedging_score': hedging['score'],  # This will be negative
            'hedging_terms': hedging['terms_found'],
            
            # Combined metrics
            'total_certainty_count': total_certainty_count,
            'total_certainty_score': total_certainty_score,
            'net_certainty_score': net_certainty_score,
            
            # Ratios and densities
            'certainty_density': (total_certainty_count / word_count * 1000) if word_count > 0 else 0,
            'hedging_density': (hedging['count'] / word_count * 1000) if word_count > 0 else 0,
            'certainty_hedging_ratio': (total_certainty_count / max(hedging['count'], 1)),
            
            'word_count': word_count,
        }
    
    def get_certainty_level(self, text):
        """
        Calculate overall certainty level (0-10 scale)
        Higher = more certainty, less hedging
        """
        results = self.analyze(text)
        
        # Based on net certainty density
        # Typical range: -5 to +15 per 1000 words
        # Scale to 0-10
        certainty_level = (results['certainty_density'] - results['hedging_density']) / 2
        certainty_level = max(0, min(certainty_level, 10))
        
        return certainty_level


# Example usage and testing
if __name__ == "__main__":
    
    detector = CertaintyDetector()
    
    # Test speeches
    high_certainty_text = """
    Make no mistake, we will succeed. I guarantee that our plan will work.
    This is absolutely certain. We must act and we shall prevail. There is
    no question that this is the right path. Obviously, we are going to win.
    Let me be clear: we will deliver results. Undoubtedly, this will work.
    """
    
    hedging_text = """
    We might be able to achieve some progress. Perhaps this approach could
    work. It seems that there may be opportunities. We should probably
    consider this carefully. It appears that we can potentially make some
    improvements. This could possibly help, though we cannot be entirely
    certain. It tends to suggest that maybe we should try.
    """
    
    print("\n" + "=" * 60)
    print("TESTING CERTAINTY DETECTOR")
    print("=" * 60)
    
    # Analyze high certainty
    high_results = detector.analyze(high_certainty_text)
    print("\nHIGH CERTAINTY TEXT:")
    print(f"  Certainty markers: {high_results['total_certainty_count']}")
    print(f"  Hedging markers: {high_results['hedging_count']}")
    print(f"  Certainty density: {high_results['certainty_density']:.2f} per 1000 words")
    print(f"  Hedging density: {high_results['hedging_density']:.2f} per 1000 words")
    print(f"  Certainty/Hedging ratio: {high_results['certainty_hedging_ratio']:.2f}")
    print(f"  Certainty level: {detector.get_certainty_level(high_certainty_text):.1f}/10")
    
    # Analyze hedging
    hedge_results = detector.analyze(hedging_text)
    print("\nHEDGING TEXT:")
    print(f"  Certainty markers: {hedge_results['total_certainty_count']}")
    print(f"  Hedging markers: {hedge_results['hedging_count']}")
    print(f"  Certainty density: {hedge_results['certainty_density']:.2f} per 1000 words")
    print(f"  Hedging density: {hedge_results['hedging_density']:.2f} per 1000 words")
    print(f"  Certainty/Hedging ratio: {hedge_results['certainty_hedging_ratio']:.2f}")
    print(f"  Certainty level: {detector.get_certainty_level(hedging_text):.1f}/10")
    
    print("\n" + "=" * 60)
    print("COMPARISON:")
    print(f"  High certainty text is {high_results['certainty_density'] / max(hedge_results['certainty_density'], 1):.1f}x more certain")
    print(f"  Hedging text has {hedge_results['hedging_density'] / max(high_results['hedging_density'], 1):.1f}x more hedging")
    print("=" * 60)
    
    print("\n✓ Tests complete!")
