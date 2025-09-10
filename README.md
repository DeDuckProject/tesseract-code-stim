# Tesseract Code

This repository contains implementations and simulations of the Tesseract quantum error correction code using Stim and PyMatching.

## Features

- Circuit implementation of the Tesseract code
- Error simulation and correction
- Jupyter notebooks with various experiments and visualizations
- Utility functions for circuit manipulation and analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/DeDuckProject/tesseract-code-stim.git
cd tesseract-code-stim

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Structure

- `circuit_commons.py`: Core circuit components and helper functions
- `stim_simulation_utils.py`: Simulation and plotting utilities
- `stim_utils.py`: Stim-specific helper functions
- Notebooks:
  - `01_stim_playground.ipynb`: Initial Stim experiments
  - `03_tesseract_stim_simulation_pymatching.ipynb`: Main simulation with PyMatching
  - `04_stim_example_5_qubit_code.ipynb`: Five-qubit code reference
  - And more...

## Usage

The main workflow is through Jupyter notebooks. After installation:

```bash
jupyter notebook
```

Then navigate to one of the notebooks to run experiments and simulations.

### Running Simulations with Noise

The `tesseract_sim/run.py` script now supports configurable noise injection during encoding and error correction phases. You can control whether noise is active and set independent 1-qubit and 2-qubit error rates for each phase.

```bash
python -m tesseract_sim.run --help
```

**Example Usages:**

*   **Run simulation with default settings (no noise):**
    ```bash
    python -m tesseract_sim.run
    ```

*   **Run simulation with encoding noise enabled (1-qubit rate 0.001, 2-qubit rate 0.002):**
    ```bash
    python -m tesseract_sim.run --enc-active --enc-rate-1q 0.001 --enc-rate-2q 0.002
    ```

*   **Run simulation with error correction noise enabled (1-qubit rate 0.003, 2-qubit rate 0.004):**
    ```bash
    python -m tesseract_sim.run --ec-active --ec-rate-1q 0.003 --ec-rate-2q 0.004
    ```

*   **Run simulation with both encoding and error correction noise:**
    ```bash
    python -m tesseract_sim.run --enc-active --enc-rate-1q 0.001 --ec-active --ec-rate-1q 0.003 --rounds 5 --shots 5000
    ```

*   **Run simulation with noise enabled but zero rates (effectively no noise):**
    ```bash
    python -m tesseract_sim.run --enc-active --enc-rate-1q 0.0 --ec-active --ec-rate-1q 0.0
    ```

### Plotting Results

The `plotting/plot_acceptance_rates.py` script generates acceptance and logical success rate plots from simulation data. It supports different encoding modes and Pauli frame correction settings.

**Example Usages:**

*   **Generate plots with Pauli frame correction enabled and 9a encoding:**
    ```bash
    python plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9a
    ```

*   **Generate plots with Pauli frame correction disabled and 9a encoding:**
    ```bash
    python plotting/plot_acceptance_rates.py --apply_pauli_frame false --encoding-mode 9a
    ```

*   **Generate plots with 9b encoding and custom shot count:**
    ```bash
    python plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9b --shots 5000
    ```

*   **Generate plots with channel noise sweep instead of EC noise:**
    ```bash
    python plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9a --sweep-channel-noise
    ```

*   **Specify custom output directory:**
    ```bash
    python plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9a --out-dir ./custom_plots
    ```

The script generates two types of plots:
- **Acceptance Rate Plots**: Show how well the error correction accepts states across different noise levels and rounds
- **Logical Success Rate Plots**: Show the conditional probability of logical success given acceptance

## License

MIT License 