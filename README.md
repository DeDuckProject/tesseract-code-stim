# Tesseract Code

This repository contains implementations and simulations of the Tesseract quantum error correction code [[1]](#references) using Stim [[3]](#references).

## Features

- Circuit implementation of the [[16,4,4]] Tesseract subsystem color code [[2]](#references) in Stim, including encoding, error correction rounds and final measurements.
- Simulation of an error correction experiment with configurable noise setting, rounds, shot and more.
- Plotting: sweeping of different parameters and obtaining acceptance rate and logical success rate.

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

TODO - fill in.

## Usage

The main workflow is through Jupyter notebooks. After installation:

```bash
jupyter notebook
```

Then navigate to one of the notebooks to run experiments and simulations.

### Running Simulations

The `tesseract_sim/run.py` script supports configurable noise injection during encoding and error correction phases. You can control whether noise is active and set independent 1-qubit and 2-qubit error rates for each phase.

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
    python tesseract_sim/plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9a
    ```

*   **Generate plots with Pauli frame correction disabled and 9a encoding:**
    ```bash
    python tesseract_sim/plotting/plot_acceptance_rates.py --apply_pauli_frame false --encoding-mode 9a
    ```

*   **Generate plots with 9b encoding and custom shot count:**
    ```bash
    python tesseract_sim/plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9b --shots 5000
    ```

*   **Generate plots with channel noise sweep instead of EC noise:**
    ```bash
    python tesseract_sim/plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9a --sweep-channel-noise
    ```

*   **Specify custom output directory:**
    ```bash
    python tesseract_sim/plotting/plot_acceptance_rates.py --apply_pauli_frame true --encoding-mode 9a --out-dir ./custom_plots
    ```

The script generates two types of plots:
- **Acceptance Rate Plots**: Show how well the error correction accepts states across different noise levels and rounds
- **Logical Success Rate Plots**: Show the conditional probability of logical success given acceptance

## References

[1] B. W. Reichardt et al., "Demonstration of quantum computation and error correction with a tesseract code", (2024) [arXiv:2409.04628](https://arxiv.org/abs/2409.04628)

[2] "\([[16,6,4]]\) Tesseract color code", The Error Correction Zoo (V. V. Albert & P. Faist, eds.), 2024. https://errorcorrectionzoo.org/c/stab_16_6_4

[3] C. Gidney, "Stim: a fast stabilizer circuit simulator", Quantum 5, 497 (2021). https://doi.org/10.22331/q-2021-07-06-497

## License

MIT License 