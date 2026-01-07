"""
Statistical Comparison Methods for Linguistic Features
Learn to test if differences between Populist and Mainstream are significant

Key Concepts:
1. T-test: Compare means of two groups
2. Effect size: How big is the difference?
3. P-value: Is the difference real or random?
"""

import numpy as np
from scipy import stats
import pandas as pd

class StatisticalTester:
    """
    Perform statistical tests comparing two groups
    """
    
    def __init__(self, alpha=0.05):
        """
        Args:
            alpha: Significance level (default 0.05 = 5%)
        """
        self.alpha = alpha
    
    def independent_t_test(self, group1, group2, feature_name="Feature"):
        """
        Independent samples t-test
        Tests if two groups have different means
        
        Use when: Comparing two independent groups (Populist vs Mainstream)
        
        Args:
            group1: List/array of values for group 1
            group2: List/array of values for group 2
            feature_name: Name of feature being tested
        
        Returns:
            dict with test results
        """
        
        # Convert to numpy arrays
        g1 = np.array(group1)
        g2 = np.array(group2)
        
        # Calculate descriptive statistics
        mean1 = np.mean(g1)
        mean2 = np.mean(g2)
        std1 = np.std(g1, ddof=1)  # Sample standard deviation
        std2 = np.std(g2, ddof=1)
        n1 = len(g1)
        n2 = len(g2)
        
        # Perform t-test
        # Two-sided test (checks if means are different in either direction)
        t_statistic, p_value = stats.ttest_ind(g1, g2)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        cohens_d = (mean1 - mean2) / pooled_std
        
        # Interpret effect size
        effect_size_interpretation = self._interpret_cohens_d(abs(cohens_d))
        
        # Determine significance
        is_significant = p_value < self.alpha
        
        return {
            'feature': feature_name,
            'group1_mean': mean1,
            'group2_mean': mean2,
            'group1_std': std1,
            'group2_std': std2,
            'group1_n': n1,
            'group2_n': n2,
            'mean_difference': mean1 - mean2,
            't_statistic': t_statistic,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'effect_size': effect_size_interpretation,
            'is_significant': is_significant,
            'alpha': self.alpha
        }
    
    def _interpret_cohens_d(self, d):
        """
        Interpret Cohen's d effect size
        
        Rules of thumb:
        - 0.2: Small effect
        - 0.5: Medium effect
        - 0.8: Large effect
        """
        if d < 0.2:
            return "Negligible"
        elif d < 0.5:
            return "Small"
        elif d < 0.8:
            return "Medium"
        else:
            return "Large"
    
    def interpret_p_value(self, p_value):
        """
        Interpret p-value in plain English
        """
        if p_value < 0.001:
            return "Very strong evidence of difference (p < 0.001)"
        elif p_value < 0.01:
            return "Strong evidence of difference (p < 0.01)"
        elif p_value < 0.05:
            return "Moderate evidence of difference (p < 0.05)"
        else:
            return "No significant evidence of difference (p ≥ 0.05)"
    
    def print_test_results(self, results):
        """
        Print test results in readable format
        """
        print(f"\nSTATISTICAL TEST: {results['feature']}")
        print("=" * 70)
        
        print(f"\nGROUP 1 (e.g., Populist):")
        print(f"  Mean:     {results['group1_mean']:8.2f}")
        print(f"  Std Dev:  {results['group1_std']:8.2f}")
        print(f"  N:        {results['group1_n']:8d}")
        
        print(f"\nGROUP 2 (e.g., Mainstream):")
        print(f"  Mean:     {results['group2_mean']:8.2f}")
        print(f"  Std Dev:  {results['group2_std']:8.2f}")
        print(f"  N:        {results['group2_n']:8d}")
        
        print(f"\nDIFFERENCE:")
        print(f"  Mean Difference: {results['mean_difference']:8.2f}")
        print(f"  Direction:       Group 1 {'higher' if results['mean_difference'] > 0 else 'lower'} than Group 2")
        
        print(f"\nSTATISTICAL SIGNIFICANCE:")
        print(f"  t-statistic:     {results['t_statistic']:8.2f}")
        print(f"  p-value:         {results['p_value']:8.4f}")
        print(f"  Significant?     {'YES ✓' if results['is_significant'] else 'NO ✗'} (α = {results['alpha']})")
        print(f"  Interpretation:  {self.interpret_p_value(results['p_value'])}")
        
        print(f"\nEFFECT SIZE:")
        print(f"  Cohen's d:       {results['cohens_d']:8.2f}")
        print(f"  Effect Size:     {results['effect_size']}")
        
        print("=" * 70)
    
    def compare_multiple_features(self, df, group_column, feature_columns, 
                                  group1_label, group2_label):
        """
        Compare multiple features at once
        
        Args:
            df: DataFrame with all data
            group_column: Column name for group labels (e.g., 'category')
            feature_columns: List of feature columns to test
            group1_label: Label for group 1 (e.g., 'Populist')
            group2_label: Label for group 2 (e.g., 'Mainstream')
        
        Returns:
            DataFrame with all test results
        """
        
        results_list = []
        
        for feature in feature_columns:
            # Extract data for each group
            group1_data = df[df[group_column] == group1_label][feature].dropna()
            group2_data = df[df[group_column] == group2_label][feature].dropna()
            
            # Run t-test
            result = self.independent_t_test(group1_data, group2_data, feature)
            results_list.append(result)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results_list)
        
        # Sort by p-value (most significant first)
        results_df = results_df.sort_values('p_value')
        
        return results_df
    
    def print_summary_table(self, results_df, group1_name="Group 1", group2_name="Group 2"):
        """
        Print summary table of multiple tests
        """
        print(f"\nSUMMARY: {group1_name} vs {group2_name}")
        print("=" * 100)
        print(f"{'Feature':<25} {group1_name+' Mean':>12} {group2_name+' Mean':>12} {'Diff':>10} {'p-value':>10} {'d':>8} {'Sig':>6}")
        print("-" * 100)
        
        for _, row in results_df.iterrows():
            sig_marker = "***" if row['p_value'] < 0.001 else "**" if row['p_value'] < 0.01 else "*" if row['p_value'] < 0.05 else ""
            
            print(f"{row['feature']:<25} {row['group1_mean']:>12.2f} {row['group2_mean']:>12.2f} "
                  f"{row['mean_difference']:>10.2f} {row['p_value']:>10.4f} {row['cohens_d']:>8.2f} {sig_marker:>6}")
        
        print("-" * 100)
        print("Significance: *** p<0.001, ** p<0.01, * p<0.05")
        print("=" * 100)


# Example usage and tutorial
if __name__ == "__main__":
    
    print("=" * 70)
    print("STATISTICAL TESTING TUTORIAL")
    print("=" * 70)
    
    # Create test data
    # Simulate: Populist speeches have higher anti-elite rhetoric
    np.random.seed(42)
    
    populist_anti_elite = np.random.normal(loc=4.5, scale=1.2, size=14)  # Mean ~4.5
    mainstream_anti_elite = np.random.normal(loc=1.8, scale=0.8, size=14)  # Mean ~1.8
    
    populist_readability = np.random.normal(loc=72, scale=8, size=14)  # Easier (higher score)
    mainstream_readability = np.random.normal(loc=58, scale=10, size=14)  # Harder (lower score)
    
    # Initialize tester
    tester = StatisticalTester(alpha=0.05)
    
    # Test 1: Anti-elite rhetoric
    print("\n\nTEST 1: ANTI-ELITE RHETORIC DENSITY")
    print("Hypothesis: Populists use MORE anti-elite rhetoric")
    
    result1 = tester.independent_t_test(
        populist_anti_elite,
        mainstream_anti_elite,
        "Anti-Elite Density"
    )
    tester.print_test_results(result1)
    
    # Test 2: Readability
    print("\n\nTEST 2: FLESCH READING EASE")
    print("Hypothesis: Populist speeches are EASIER to read (higher score)")
    
    result2 = tester.independent_t_test(
        populist_readability,
        mainstream_readability,
        "Flesch Reading Ease"
    )
    tester.print_test_results(result2)
    
    # Multiple features comparison
    print("\n\n" + "=" * 70)
    print("MULTIPLE FEATURES COMPARISON")
    print("=" * 70)
    
    # Create sample DataFrame
    data = {
        'category': ['Populist'] * 14 + ['Mainstream'] * 14,
        'anti_elite_density': list(populist_anti_elite) + list(mainstream_anti_elite),
        'flesch_reading_ease': list(populist_readability) + list(mainstream_readability),
        'we_they_ratio': list(np.random.normal(2.5, 0.5, 14)) + list(np.random.normal(6.0, 1.2, 14)),
        'crisis_density': list(np.random.normal(8.5, 2.0, 14)) + list(np.random.normal(4.2, 1.5, 14))
    }
    
    df = pd.DataFrame(data)
    
    # Test all features
    features_to_test = ['anti_elite_density', 'flesch_reading_ease', 'we_they_ratio', 'crisis_density']
    
    results_df = tester.compare_multiple_features(
        df, 
        group_column='category',
        feature_columns=features_to_test,
        group1_label='Populist',
        group2_label='Mainstream'
    )
    
    # Print summary
    tester.print_summary_table(results_df, "Populist", "Mainstream")
    
    print("\n" + "=" * 70)
    print("KEY CONCEPTS:")
    print("=" * 70)
    print("""
1. P-VALUE: Probability that the difference is due to chance
   - p < 0.05: Significant (less than 5% chance it's random)
   - p < 0.01: Very significant
   - p < 0.001: Extremely significant
   
2. EFFECT SIZE (Cohen's d): How big is the difference?
   - d = 0.2: Small
   - d = 0.5: Medium  
   - d = 0.8: Large
   - Important: A result can be significant but have small effect size!
   
3. T-STATISTIC: How many standard deviations apart are the means?
   - Larger absolute value = stronger evidence of difference
   
4. FOR YOUR ASSIGNMENT:
   "Populist speeches exhibited significantly higher anti-elite rhetoric 
   (M=4.5, SD=1.2) compared to mainstream speeches (M=1.8, SD=0.8), 
   t(26)=7.23, p<0.001, d=2.65, representing a large effect size."
    """)
    
    print("\n✓ Tutorial complete!")
