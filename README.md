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

## License

MIT License 