"""
Pronoun Analysis for In-Group/Out-Group Framing
Extracts and categorizes pronouns to measure us-vs-them rhetoric

Key Populist Pattern:
- High "we/us/our" (in-group solidarity)
- High "they/them/their" (out-group othering)
- High ratio = strong us-vs-them framing
"""

import re
from collections import Counter

class PronounAnalyzer:
    """
    Analyze pronoun usage for in-group/out-group framing
    
    Categories:
    1. First person plural (WE): we, us, our, ours, ourselves
    2. First person singular (I): I, me, my, mine, myself
    3. Third person plural (THEY): they, them, their, theirs, themselves
    4. Second person (YOU): you, your, yours, yourself, yourselves
    """
    
    def __init__(self):
        # In-group pronouns (WE - inclusive, solidarity)
        self.we_pronouns = {
            'we', 'us', 'our', 'ours', 'ourselves'
        }
        
        # Individual leader (I - personal authority)
        self.i_pronouns = {
            'i', 'me', 'my', 'mine', 'myself'
        }
        
        # Out-group pronouns (THEY - othering, exclusion)
        self.they_pronouns = {
            'they', 'them', 'their', 'theirs', 'themselves'
        }
        
        # Direct address (YOU - appeals to audience)
        self.you_pronouns = {
            'you', 'your', 'yours', 'yourself', 'yourselves'
        }
        
        # All pronouns
        self.all_pronouns = (
            self.we_pronouns | self.i_pronouns | 
            self.they_pronouns | self.you_pronouns
        )
    
    def tokenize(self, text):
        """
        Simple tokenization - split on whitespace and punctuation
        """
        # Convert to lowercase
        text = text.lower()
        
        # Replace punctuation with spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        return words
    
    def extract_pronouns(self, text):
        """
        Extract all pronouns from text
        Returns dict with counts for each category
        """
        words = self.tokenize(text)
        
        # Count each category
        we_count = sum(1 for w in words if w in self.we_pronouns)
        i_count = sum(1 for w in words if w in self.i_pronouns)
        they_count = sum(1 for w in words if w in self.they_pronouns)
        you_count = sum(1 for w in words if w in self.you_pronouns)
        
        # Detailed counts
        we_detailed = Counter(w for w in words if w in self.we_pronouns)
        i_detailed = Counter(w for w in words if w in self.i_pronouns)
        they_detailed = Counter(w for w in words if w in self.they_pronouns)
        you_detailed = Counter(w for w in words if w in self.you_pronouns)
        
        total_pronouns = we_count + i_count + they_count + you_count
        word_count = len(words)
        
        return {
            'we_count': we_count,
            'i_count': i_count,
            'they_count': they_count,
            'you_count': you_count,
            'total_pronouns': total_pronouns,
            'word_count': word_count,
            
            # Detailed breakdowns
            'we_detailed': dict(we_detailed),
            'i_detailed': dict(i_detailed),
            'they_detailed': dict(they_detailed),
            'you_detailed': dict(you_detailed),
        }
    
    def analyze(self, text):
        """
        Full pronoun analysis with ratios and metrics
        """
        results = self.extract_pronouns(text)
        
        # Calculate densities (per 1000 words)
        word_count = results['word_count']
        we_density = (results['we_count'] / word_count * 1000) if word_count > 0 else 0
        i_density = (results['i_count'] / word_count * 1000) if word_count > 0 else 0
        they_density = (results['they_count'] / word_count * 1000) if word_count > 0 else 0
        you_density = (results['you_count'] / word_count * 1000) if word_count > 0 else 0
        
        # Calculate key ratios
        
        # 1. We/They ratio (in-group vs out-group)
        # High ratio = strong "us vs them" framing
        we_they_ratio = results['we_count'] / max(results['they_count'], 1)
        
        # 2. We/I ratio (collective vs individual)
        # High ratio = emphasizes collective, low ratio = emphasizes leader
        we_i_ratio = results['we_count'] / max(results['i_count'], 1)
        
        # 3. Collective pronouns (we + you) vs exclusive (they)
        # Populists often use "we" and "you" to build solidarity, "they" to other
        inclusive = results['we_count'] + results['you_count']
        exclusive = results['they_count']
        inclusive_exclusive_ratio = inclusive / max(exclusive, 1)
        
        # 4. Pronoun diversity - what % of pronouns are each type?
        total_p = results['total_pronouns']
        we_pct = (results['we_count'] / total_p * 100) if total_p > 0 else 0
        i_pct = (results['i_count'] / total_p * 100) if total_p > 0 else 0
        they_pct = (results['they_count'] / total_p * 100) if total_p > 0 else 0
        you_pct = (results['you_count'] / total_p * 100) if total_p > 0 else 0
        
        return {
            **results,
            
            # Densities
            'we_density': we_density,
            'i_density': i_density,
            'they_density': they_density,
            'you_density': you_density,
            'total_pronoun_density': (total_p / word_count * 1000) if word_count > 0 else 0,
            
            # Ratios
            'we_they_ratio': we_they_ratio,
            'we_i_ratio': we_i_ratio,
            'inclusive_exclusive_ratio': inclusive_exclusive_ratio,
            
            # Percentages
            'we_pct': we_pct,
            'i_pct': i_pct,
            'they_pct': they_pct,
            'you_pct': you_pct,
        }
    
    def get_framing_score(self, text):
        """
        Calculate overall us-vs-them framing intensity (0-10 scale)
        
        High score = strong in-group/out-group division
        """
        results = self.analyze(text)
        
        # Combine multiple signals:
        # 1. High we+you density (building solidarity)
        # 2. High they density (othering)
        # 3. High we/they ratio (emphasis on division)
        
        inclusive_density = results['we_density'] + results['you_density']
        they_density = results['they_density']
        
        # Score based on presence of both in-group and out-group
        # Perfect framing has both high "we" and high "they"
        
        if inclusive_density > 20 and they_density > 10:
            framing_score = 10  # Strong us-vs-them
        elif inclusive_density > 15 and they_density > 7:
            framing_score = 7
        elif inclusive_density > 10 and they_density > 5:
            framing_score = 5
        elif inclusive_density > 5 or they_density > 3:
            framing_score = 3
        else:
            framing_score = 1
        
        return framing_score


def create_pronoun_summary(results):
    """
    Create human-readable summary of pronoun analysis
    """
    summary = f"""
PRONOUN ANALYSIS SUMMARY
{'=' * 60}

RAW COUNTS:
  We/us/our:       {results['we_count']:4d}
  I/me/my:         {results['i_count']:4d}
  They/them/their: {results['they_count']:4d}
  You/your:        {results['you_count']:4d}
  Total pronouns:  {results['total_pronouns']:4d}

DENSITIES (per 1000 words):
  We:   {results['we_density']:6.2f}
  I:    {results['i_density']:6.2f}
  They: {results['they_density']:6.2f}
  You:  {results['you_density']:6.2f}

KEY RATIOS:
  We/They ratio:  {results['we_they_ratio']:.2f}  {'(Strong in-group focus)' if results['we_they_ratio'] > 2 else ''}
  We/I ratio:     {results['we_i_ratio']:.2f}  {'(Collective emphasis)' if results['we_i_ratio'] > 2 else '(Individual emphasis)' if results['we_i_ratio'] < 0.5 else ''}

DISTRIBUTION:
  We:   {results['we_pct']:.1f}% of pronouns
  I:    {results['i_pct']:.1f}% of pronouns
  They: {results['they_pct']:.1f}% of pronouns
  You:  {results['you_pct']:.1f}% of pronouns

{'=' * 60}
    """
    return summary


# Example usage and testing
if __name__ == "__main__":
    
    analyzer = PronounAnalyzer()
    
    # Test speeches
    populist_text = """
    We are the people and they have ignored us for too long. They sit in their
    ivory towers while we struggle. We will take back control. They don't care
    about us, but we care about our country. Together, we will succeed where
    they have failed. You and I, we are in this together. They want to stop us,
    but we won't let them. Our voice will be heard. We are the majority and
    they are the elite. We will prevail.
    """
    
    mainstream_text = """
    I am committed to delivering strong economic growth. Our government has
    implemented responsible policies. I believe we can achieve prosperity through
    careful management. My administration will continue to work diligently. We
    have made progress and I am confident in our direction. The economy is stable
    and we will maintain this trajectory. I assure you that our approach is sound.
    """
    
    print("\n" + "=" * 70)
    print("TESTING PRONOUN ANALYZER")
    print("=" * 70)
    
    # Analyze populist text
    print("\nPOPULIST TEXT ANALYSIS:")
    pop_results = analyzer.analyze(populist_text)
    print(create_pronoun_summary(pop_results))
    print(f"Us-vs-Them Framing Score: {analyzer.get_framing_score(populist_text)}/10")
    
    # Analyze mainstream text
    print("\nMAINSTREAM TEXT ANALYSIS:")
    main_results = analyzer.analyze(mainstream_text)
    print(create_pronoun_summary(main_results))
    print(f"Us-vs-Them Framing Score: {analyzer.get_framing_score(mainstream_text)}/10")
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON:")
    print("=" * 70)
    print(f"\nWe/They Ratio:")
    print(f"  Populist:   {pop_results['we_they_ratio']:.2f}")
    print(f"  Mainstream: {main_results['we_they_ratio']:.2f}")
    print(f"  Difference: {pop_results['we_they_ratio'] - main_results['we_they_ratio']:+.2f}")
    
    print(f"\nThey Density (per 1000):")
    print(f"  Populist:   {pop_results['they_density']:.2f}")
    print(f"  Mainstream: {main_results['they_density']:.2f}")
    print(f"  Difference: {pop_results['they_density'] - main_results['they_density']:+.2f}")
    
    print("\n" + "=" * 70)
    print("✓ Tests complete!")
