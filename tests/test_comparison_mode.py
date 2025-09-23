"""Test for comparison mode functionality in plot_acceptance_rates.py"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from tesseract_sim.plotting.plot_acceptance_rates import plot_ec_experiment, plot_curve
from tesseract_sim.noise.noise_cfg import NoiseCfg


def test_plot_ec_experiment_backwards_compatibility():
    """Test that plot_ec_experiment works without comparison_mode parameter (backwards compatibility)"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the sweep_results and run_simulation_ec_experiment to avoid actual computation
        mock_results = {
            0.001: [(100, 95, 0.98), (100, 90, 0.97)]  # (accepted, logical_pass, avg_fidelity)
        }
        
        with patch('tesseract_sim.plotting.plot_acceptance_rates.sweep_results', return_value=mock_results):
            with patch('matplotlib.pyplot.savefig'):
                with patch('matplotlib.pyplot.close'):
                    # Should work without comparison_mode parameter
                    plot_ec_experiment(
                        rounds=[1, 2],
                        noise_levels=[0.001],
                        shots=100,
                        base_out_dir=temp_dir,
                        apply_pauli_frame=True,
                        encoding_mode='9b'
                    )


def test_plot_ec_experiment_comparison_mode():
    """Test that comparison mode runs both experiments"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the sweep_results to return different results for each call
        mock_results_with = {
            0.001: [(100, 95, 0.98), (100, 90, 0.97)]
        }
        mock_results_without = {
            0.001: [(100, 85, 0.95), (100, 80, 0.93)]
        }
        
        with patch('tesseract_sim.plotting.plot_acceptance_rates.sweep_results') as mock_sweep:
            # Configure mock to return different results for each call
            mock_sweep.side_effect = [mock_results_with, mock_results_without]
            
            with patch('matplotlib.pyplot.savefig'):
                with patch('matplotlib.pyplot.close'):
                    plot_ec_experiment(
                        rounds=[1, 2],
                        noise_levels=[0.001],
                        shots=100,
                        base_out_dir=temp_dir,
                        apply_pauli_frame=True,  # This will be ignored in comparison mode
                        encoding_mode='9b',
                        comparison_mode=True
                    )
            
            # Verify sweep_results was called twice (once with True, once with False)
            assert mock_sweep.call_count == 2
            calls = mock_sweep.call_args_list
            
            # First call should have apply_pauli_frame=True
            assert calls[0][1]['apply_pauli_frame'] is True
            # Second call should have apply_pauli_frame=False
            assert calls[1][1]['apply_pauli_frame'] is False


def test_plot_curve_with_comparison():
    """Test that plot_curve handles comparison data correctly"""
    rounds = [1, 2, 3]
    main_data = {0.001: [0.9, 0.85, 0.8]}
    comparison_data = {0.001: [0.95, 0.9, 0.85]}
    
    with patch('matplotlib.pyplot.figure'):
        with patch('matplotlib.pyplot.plot') as mock_plot:
            with patch('matplotlib.pyplot.savefig'):
                with patch('matplotlib.pyplot.close'):
                    with patch('matplotlib.pyplot.xlabel'):
                        with patch('matplotlib.pyplot.ylabel'):
                            with patch('matplotlib.pyplot.title'):
                                with patch('matplotlib.pyplot.grid'):
                                    with patch('matplotlib.pyplot.legend'):
                                        plot_curve(
                                            rounds=rounds,
                                            data=main_data,
                                            title="Test",
                                            ylabel="Test Y",
                                            out_path="test.png",
                                            comparison_data=comparison_data,
                                            comparison_label="without correction"
                                        )
    
    # Verify plot was called twice (once for main data, once for comparison)
    assert mock_plot.call_count == 2
    
    # Check that different line styles were used
    calls = mock_plot.call_args_list
    main_call_kwargs = calls[0][1]
    comparison_call_kwargs = calls[1][1]
    
    assert main_call_kwargs['linestyle'] == '-'  # solid line
    assert comparison_call_kwargs['linestyle'] == '--'  # dashed line
    assert main_call_kwargs['marker'] == 'o'
    assert comparison_call_kwargs['marker'] == 's'  # square marker


if __name__ == "__main__":
    test_plot_ec_experiment_backwards_compatibility()
    test_plot_ec_experiment_comparison_mode()
    test_plot_curve_with_comparison()
    print("All tests passed!")
