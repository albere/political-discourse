"""
Crisis Language Detector
Identifies crisis framing and urgency rhetoric in political speeches

Crisis framing is a key populist strategy: presenting the current situation
as an emergency that requires immediate, drastic action.
"""

from collections import Counter
import re

class CrisisDetector:
    """
    Detects crisis framing and emergency rhetoric in political speeches
    
    Categories:
    1. Crisis/emergency terms (explicit crisis framing)
    2. Threat language (danger, risk, fear)
    3. Decline/deterioration framing (things getting worse)
    4. Urgency markers (time pressure, immediate action needed)
    5. Catastrophic language (extreme negative outcomes)
    """
    
    def __init__(self):
        # Explicit crisis terms
        self.crisis_terms = {
            'crisis': 3.0,
            'crises': 3.0,
            'emergency': 3.0,
            'catastrophe': 4.0,
            'catastrophic': 4.0,
            'disaster': 3.5,
            'disastrous': 3.5,
            'chaos': 3.0,
            'chaotic': 2.5,
            'breakdown': 2.5,
            'collapse': 3.0,
            'collapsing': 3.0,
        }
        
        # Threat and danger language
        self.threat_terms = {
            'threat': 2.5,
            'threatens': 2.5,
            'threatening': 2.5,
            'threatened': 2.5,
            'danger': 2.5,
            'dangerous': 2.5,
            'dangerously': 2.5,
            'risk': 2.0,
            'risks': 2.0,
            'at risk': 2.5,
            'under threat': 3.0,
            'under attack': 3.0,
            'attack': 2.0,
            'attacking': 2.0,
            'fear': 2.0,
            'fears': 2.0,
            'terrify': 2.5,
            'terrifying': 2.5,
            'alarm': 2.0,
            'alarming': 2.5,
        }
        
        # Decline and deterioration
        self.decline_terms = {
            'decline': 2.0,
            'declining': 2.0,
            'deteriorate': 2.5,
            'deteriorating': 2.5,
            'deterioration': 2.5,
            'worse': 1.5,
            'worsen': 2.0,
            'worsening': 2.0,
            'falling apart': 3.0,
            'fall apart': 3.0,
            'breaking down': 2.5,
            'break down': 2.5,
            'spiral': 2.0,
            'spiraling': 2.5,
            'out of control': 3.0,
            'losing control': 2.5,
        }
        
        # Urgency markers (time pressure)
        self.urgency_terms = {
            'urgent': 2.5,
            'urgently': 2.5,
            'urgency': 2.5,
            'immediate': 2.0,
            'immediately': 2.0,
            'now': 1.5,
            'right now': 2.0,
            'must act': 2.5,
            'act now': 2.5,
            'time is running out': 3.0,
            'running out of time': 3.0,
            'no time': 2.5,
            'cannot wait': 2.5,
            'can\'t wait': 2.5,
            'before it\'s too late': 3.0,
            'too late': 2.0,
        }
        
        # Catastrophic outcomes
        self.catastrophic_terms = {
            'destroy': 2.5,
            'destroying': 2.5,
            'destruction': 3.0,
            'devastate': 3.0,
            'devastating': 3.0,
            'devastation': 3.0,
            'ruin': 2.5,
            'ruined': 2.5,
            'ruining': 2.5,
            'irreversible': 3.0,
            'point of no return': 3.5,
            'no going back': 3.0,
            'existential': 3.5,
            'existential threat': 4.0,
            'survival': 2.5,
            'survive': 2.0,
        }
        
        # All terms combined
        self.all_terms = {
            **self.crisis_terms,
            **self.threat_terms,
            **self.decline_terms,
            **self.urgency_terms,
            **self.catastrophic_terms
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
        Full crisis language analysis
        
        Returns:
            dict with counts, scores, and density metrics
        """
        word_count = len(text.split())
        
        # Analyze each category
        crisis = self.count_terms(text, self.crisis_terms)
        threat = self.count_terms(text, self.threat_terms)
        decline = self.count_terms(text, self.decline_terms)
        urgency = self.count_terms(text, self.urgency_terms)
        catastrophic = self.count_terms(text, self.catastrophic_terms)
        
        # Combined totals
        total_count = (crisis['count'] + threat['count'] + decline['count'] + 
                      urgency['count'] + catastrophic['count'])
        total_score = (crisis['score'] + threat['score'] + decline['score'] + 
                      urgency['score'] + catastrophic['score'])
        
        return {
            # Crisis terms
            'crisis_count': crisis['count'],
            'crisis_score': crisis['score'],
            'crisis_terms': crisis['terms_found'],
            
            # Threat language
            'threat_count': threat['count'],
            'threat_score': threat['score'],
            'threat_terms': threat['terms_found'],
            
            # Decline framing
            'decline_count': decline['count'],
            'decline_score': decline['score'],
            'decline_terms': decline['terms_found'],
            
            # Urgency markers
            'urgency_count': urgency['count'],
            'urgency_score': urgency['score'],
            'urgency_terms': urgency['terms_found'],
            
            # Catastrophic language
            'catastrophic_count': catastrophic['count'],
            'catastrophic_score': catastrophic['score'],
            'catastrophic_terms': catastrophic['terms_found'],
            
            # Combined metrics
            'total_crisis_count': total_count,
            'total_crisis_score': total_score,
            'crisis_density': (total_count / word_count * 1000) if word_count > 0 else 0,
            'word_count': word_count,
        }
    
    def get_crisis_intensity(self, text):
        """
        Calculate overall crisis intensity score (0-10 scale)
        """
        results = self.analyze(text)
        
        # Normalize to 0-10 scale based on density
        # Typical range: 0-20 per 1000 words, scale to 0-10
        intensity = min(results['crisis_density'] / 2, 10)
        
        return intensity


# Example usage and testing
if __name__ == "__main__":
    
    detector = CrisisDetector()
    
    # Test speeches
    crisis_text = """
    We face a catastrophic crisis. Our country is under threat and time is
    running out. The system is collapsing and chaos threatens everything we
    hold dear. This is an existential emergency. We must act now before it's
    too late. The situation is deteriorating rapidly and the risks are 
    alarming. Our survival is at stake.
    """
    
    no_crisis_text = """
    Our government continues to deliver steady progress. Through careful
    management and sound policies, we are building a stronger economy.
    We remain committed to creating opportunities for all families. Our
    approach is working and we will continue on this stable path.
    """
    
    print("\n" + "=" * 60)
    print("TESTING CRISIS LANGUAGE DETECTOR")
    print("=" * 60)
    
    # Analyze crisis text
    crisis_results = detector.analyze(crisis_text)
    print("\nCRISIS-FRAMED TEXT:")
    print(f"  Total crisis terms: {crisis_results['total_crisis_count']}")
    print(f"  Crisis density: {crisis_results['crisis_density']:.2f} per 1000 words")
    print(f"  Crisis intensity: {detector.get_crisis_intensity(crisis_text):.1f}/10")
    print(f"\n  Breakdown:")
    print(f"    Explicit crisis: {crisis_results['crisis_count']}")
    print(f"    Threat language: {crisis_results['threat_count']}")
    print(f"    Decline framing: {crisis_results['decline_count']}")
    print(f"    Urgency markers: {crisis_results['urgency_count']}")
    print(f"    Catastrophic: {crisis_results['catastrophic_count']}")
    
    # Analyze non-crisis text
    no_crisis_results = detector.analyze(no_crisis_text)
    print("\nNON-CRISIS TEXT:")
    print(f"  Total crisis terms: {no_crisis_results['total_crisis_count']}")
    print(f"  Crisis density: {no_crisis_results['crisis_density']:.2f} per 1000 words")
    print(f"  Crisis intensity: {detector.get_crisis_intensity(no_crisis_text):.1f}/10")
    
    print("\n" + "=" * 60)
    print(f"Crisis text has {crisis_results['crisis_density'] / max(no_crisis_results['crisis_density'], 0.1):.1f}x more crisis language")
    print("=" * 60)
    
    print("\n✓ Tests complete!")
