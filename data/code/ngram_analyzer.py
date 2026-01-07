"""
Improved N-gram Analyzer with Filtering
Removes common speech artifacts and meaningless phrases
"""

from collections import Counter
import re

class ImprovedNgramAnalyzer:
    """
    N-gram analyzer with stoplist for filtering artifacts
    """
    
    def __init__(self, min_frequency=5):
        self.min_frequency = min_frequency
        
        # Stoplist for bigrams/trigrams to exclude
        self.bigram_stoplist = {
            ('thank', 'you'),
            ('you', 'thank'),
            ('you', 'very'),
            ('very', 'much'),
            ('very', 'very'),
            ('thank', 'thank'),
            # Add more as needed
        }
        
        self.trigram_stoplist = {
            ('thank', 'you', 'very'),
            ('you', 'very', 'much'),
            ('you', 'thank', 'you'),
            ('thank', 'you', 'thank'),
            ('very', 'very', 'much'),
            # Add more as needed
        }
        
        # Words to filter out entirely (website artifacts, etc.)
        self.word_blacklist = {
            'aa', 'rr', 'mmeerriiccaann', 'hheettoorriicc', 
            'ccoomm', 'americanrhetoric', 'property',
            'copyright', 'transcript', 'video', 'audio'
        }
    
    def tokenize(self, text):
        """Tokenize with filtering"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter out blacklisted words
        words = [w for w in words if w and len(w) > 1 and w not in self.word_blacklist]
        
        return words
    
    def extract_ngrams(self, words, n):
        """Extract n-grams"""
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = tuple(words[i:i+n])
            ngrams.append(ngram)
        return ngrams
    
    def filter_ngrams(self, ngrams, n):
        """Filter out stoplist n-grams"""
        stoplist = self.bigram_stoplist if n == 2 else self.trigram_stoplist
        
        filtered = []
        for ngram in ngrams:
            # Check if in stoplist
            if ngram not in stoplist:
                # Check if contains only content words (not all function words)
                if self._is_content_ngram(ngram):
                    filtered.append(ngram)
        
        return filtered
    
    def _is_content_ngram(self, ngram):
        """
        Check if n-gram contains at least some content
        Filter out pure function word sequences
        """
        function_words = {
            'the', 'of', 'to', 'and', 'in', 'that', 'is', 'was', 
            'for', 'on', 'with', 'as', 'by', 'at', 'from', 'this',
            'be', 'are', 'an', 'or', 'but', 'not', 'if', 'so'
        }
        
        # At least one word should not be a function word
        content_count = sum(1 for word in ngram if word not in function_words)
        
        # For bigrams: at least 1 content word
        # For trigrams: at least 2 content words
        min_content = 1 if len(ngram) == 2 else 2
        
        return content_count >= min_content
    
    def get_top_ngrams(self, text, n=2, top_k=20):
        """Get top n-grams with filtering"""
        words = self.tokenize(text)
        ngrams = self.extract_ngrams(words, n)
        
        # Filter
        ngrams = self.filter_ngrams(ngrams, n)
        
        # Count
        ngram_counts = Counter(ngrams)
        filtered = {ng: count for ng, count in ngram_counts.items() 
                   if count >= self.min_frequency}
        
        top_ngrams = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return top_ngrams
    
    def compare_corpora(self, corpus1, corpus2, n=2, top_k=20):
        """Compare with filtering"""
        # Get all n-grams
        ngrams1 = []
        ngrams2 = []
        
        for text in corpus1:
            words = self.tokenize(text)
            ng = self.extract_ngrams(words, n)
            ng = self.filter_ngrams(ng, n)
            ngrams1.extend(ng)
        
        for text in corpus2:
            words = self.tokenize(text)
            ng = self.extract_ngrams(words, n)
            ng = self.filter_ngrams(ng, n)
            ngrams2.extend(ng)
        
        # Count
        counts1 = Counter(ngrams1)
        counts2 = Counter(ngrams2)
        
        # Calculate distinctive
        distinctive1 = {}
        for ngram, count1 in counts1.items():
            if count1 >= self.min_frequency:
                count2 = counts2.get(ngram, 0)
                ratio = count1 / (count2 + 1)
                if ratio > 2:
                    distinctive1[ngram] = (count1, count2, ratio)
        
        distinctive2 = {}
        for ngram, count2 in counts2.items():
            if count2 >= self.min_frequency:
                count1 = counts1.get(ngram, 0)
                ratio = count2 / (count1 + 1)
                if ratio > 2:
                    distinctive2[ngram] = (count2, count1, ratio)
        
        # Common
        common_ngrams = set(counts1.keys()) & set(counts2.keys())
        common = [(ng, counts1[ng], counts2[ng]) for ng in common_ngrams 
                 if counts1[ng] >= self.min_frequency and counts2[ng] >= self.min_frequency]
        common.sort(key=lambda x: x[1] + x[2], reverse=True)
        
        # Sort by ratio
        distinctive1_sorted = sorted(distinctive1.items(), 
                                    key=lambda x: x[1][2], reverse=True)[:top_k]
        distinctive2_sorted = sorted(distinctive2.items(), 
                                    key=lambda x: x[1][2], reverse=True)[:top_k]
        
        return {
            'corpus1_distinctive': distinctive1_sorted,
            'corpus2_distinctive': distinctive2_sorted,
            'common': common[:top_k]
        }


# Test
if __name__ == "__main__":
    analyzer = ImprovedNgramAnalyzer(min_frequency=3)
    
    test_text = """
    Thank you very much. Thank you. You know, we got to take back control.
    Joe Biden has failed. The border is a crisis. Thank you very very much.
    We got to finish this. They're going to do nothing. Brexit party stands strong.
    """
    
    print("TESTING IMPROVED ANALYZER:")
    print("=" * 70)
    
    bigrams = analyzer.get_top_ngrams(test_text, n=2, top_k=10)
    print("\nBIGRAMS (filtered):")
    for ngram, count in bigrams:
        print(f"  {' '.join(ngram):30s} {count}")
    
    trigrams = analyzer.get_top_ngrams(test_text, n=3, top_k=10)
    print("\nTRIGRAMS (filtered):")
    for ngram, count in trigrams:
        print(f"  {' '.join(ngram):30s} {count}")
    
    print("\n✓ Notice 'thank you' phrases are filtered out!")
