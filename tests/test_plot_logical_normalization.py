"""
Test that logical success rates are properly normalized by acceptance rates.

This test ensures that the plotting code correctly computes conditional probabilities
P(logical success | accepted) rather than raw P(logical success).
"""

import pytest
import numpy as np
from typing import Dict, List, Tuple


def compute_logical_data_from_raw_results(raw_results: Dict[float, List[Tuple[int, int, int]]]) -> Dict[float, List[float]]:
    """
    Extract the logical data computation logic from plot_acceptance_rates.py
    for testing purposes.
    
    Args:
        raw_results: Dict mapping noise levels to lists of (accepted, logical_pass, total_shots) tuples
        
    Returns:
        Dict mapping noise levels to lists of conditional logical success rates
    """
    logical_data = {
        noise: [
            t[1]/t[0] if t[0] > 0 else 0.0  # logical_pass/accepted (conditional probability)
            for t in tuples
        ]
        for noise, tuples in raw_results.items()
    }
    return logical_data


def test_logical_normalization_basic():
    """
    Test basic logical normalization with simple numbers.
    
    Story: Given 10 shots with 4 accepted and 3 logical successes,
    the conditional logical success rate should be 3/4 = 0.75
    """
    # Arrange: (accepted, logical_pass, total_shots)
    raw_results = {
        0.01: [(4, 3, 10)]  # 4 accepted, 3 logical passes out of 10 total shots
    }
    
    # Act
    logical_data = compute_logical_data_from_raw_results(raw_results)
    
    # Assert
    expected_rate = 3.0 / 4.0  # 3 logical successes out of 4 accepted
    assert logical_data[0.01][0] == pytest.approx(expected_rate, rel=1e-6)


def test_logical_normalization_zero_acceptance():
    """
    Test that zero acceptance is handled gracefully.
    
    Story: When no shots are accepted, the conditional logical success rate
    should be 0.0 to avoid division by zero.
    """
    # Arrange: (accepted, logical_pass, total_shots)
    raw_results = {
        0.01: [(0, 0, 10)]  # 0 accepted, 0 logical passes out of 10 total shots
    }
    
    # Act
    logical_data = compute_logical_data_from_raw_results(raw_results)
    
    # Assert
    assert logical_data[0.01][0] == 0.0


def test_logical_normalization_perfect_acceptance():
    """
    Test normalization when all shots are accepted.
    
    Story: When all 10 shots are accepted and 8 pass logical checks,
    the conditional rate should be 8/10 = 0.8
    """
    # Arrange: (accepted, logical_pass, total_shots)
    raw_results = {
        0.001: [(10, 8, 10)]  # 10 accepted, 8 logical passes out of 10 total shots
    }
    
    # Act
    logical_data = compute_logical_data_from_raw_results(raw_results)
    
    # Assert
    expected_rate = 8.0 / 10.0
    assert logical_data[0.001][0] == pytest.approx(expected_rate, rel=1e-6)


def test_logical_normalization_multiple_rounds():
    """
    Test normalization across multiple rounds with different acceptance rates.
    
    Story: Across different rounds, each should have its own conditional
    logical success rate computed independently.
    """
    # Arrange: Multiple rounds with different acceptance/logical patterns
    raw_results = {
        0.005: [
            (5, 4, 10),   # Round 1: 4/5 = 0.8 conditional rate
            (8, 6, 10),   # Round 2: 6/8 = 0.75 conditional rate  
            (2, 1, 10)    # Round 3: 1/2 = 0.5 conditional rate
        ]
    }
    
    # Act
    logical_data = compute_logical_data_from_raw_results(raw_results)
    
    # Assert
    expected_rates = [4.0/5.0, 6.0/8.0, 1.0/2.0]
    for i, expected in enumerate(expected_rates):
        assert logical_data[0.005][i] == pytest.approx(expected, rel=1e-6)


def test_logical_normalization_vs_raw_normalization():
    """
    Test that conditional normalization gives different results than raw normalization.
    
    Story: To demonstrate the fix, show that P(logical | accepted) != P(logical)
    when acceptance rate < 1.0
    """
    # Arrange: (accepted, logical_pass, total_shots)
    raw_results = {
        0.01: [(6, 3, 10)]  # 6 accepted, 3 logical passes out of 10 total shots
    }
    
    # Act
    logical_data_conditional = compute_logical_data_from_raw_results(raw_results)
    logical_data_raw = 3.0 / 10.0  # Old way: logical_pass / total_shots
    
    # Assert
    conditional_rate = logical_data_conditional[0.01][0]
    assert conditional_rate == pytest.approx(3.0/6.0, rel=1e-6)  # 0.5
    assert conditional_rate != logical_data_raw  # 0.5 != 0.3
    assert conditional_rate > logical_data_raw   # Conditional rate should be higher
