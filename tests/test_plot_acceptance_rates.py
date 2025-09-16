import pytest
from tesseract_sim.plotting.plot_acceptance_rates import compute_logical_success_rate, compute_average_fidelity


class TestPlottingHelpers:
    """Test the helper functions for extracting data from raw results."""

    def test_compute_logical_success_rate_basic(self):
        """Test logical success rate computation with basic data."""
        raw_results = {
            0.1: [(10, 5, 0.6), (20, 20, 1.0)],
            0.2: [(8, 4, 0.5), (16, 12, 0.75)]
        }
        
        result = compute_logical_success_rate(raw_results)
        
        # For noise 0.1: 5/10=0.5, 20/20=1.0
        assert result[0.1] == [0.5, 1.0]
        # For noise 0.2: 4/8=0.5, 12/16=0.75
        assert result[0.2] == [0.5, 0.75]

    def test_compute_logical_success_rate_zero_accepted(self):
        """Test logical success rate when no experiments were accepted."""
        raw_results = {
            0.5: [(0, 0, 0.0), (10, 5, 0.8)]
        }
        
        result = compute_logical_success_rate(raw_results)
        
        # When accepted=0, should return 0.0, not division by zero
        assert result[0.5] == [0.0, 0.5]

    def test_compute_average_fidelity_basic(self):
        """Test average fidelity extraction with basic data."""
        raw_results = {
            0.1: [(10, 5, 0.6), (20, 20, 1.0)],
            0.2: [(8, 4, 0.5), (16, 12, 0.75)]
        }
        
        result = compute_average_fidelity(raw_results)
        
        # Should extract t[2] values directly
        assert result[0.1] == [0.6, 1.0]
        assert result[0.2] == [0.5, 0.75]

    def test_compute_average_fidelity_edge_values(self):
        """Test average fidelity with edge case values."""
        raw_results = {
            0.0: [(100, 100, 1.0), (50, 25, 0.0)],
            1.0: [(1, 0, 0.123), (0, 0, 0.456)]
        }
        
        result = compute_average_fidelity(raw_results)
        
        assert result[0.0] == [1.0, 0.0]
        assert result[1.0] == [0.123, 0.456]

    def test_empty_results(self):
        """Test both functions with empty input."""
        raw_results = {}
        
        logical_result = compute_logical_success_rate(raw_results)
        fidelity_result = compute_average_fidelity(raw_results)
        
        assert logical_result == {}
        assert fidelity_result == {}

    def test_single_noise_level(self):
        """Test both functions with single noise level and single data point."""
        raw_results = {
            0.05: [(100, 80, 0.95)]
        }
        
        logical_result = compute_logical_success_rate(raw_results)
        fidelity_result = compute_average_fidelity(raw_results)
        
        assert logical_result[0.05] == [0.8]  # 80/100
        assert fidelity_result[0.05] == [0.95]
