# Tesseract Code Stim Circuit Files

This directory contains pre-generated stim circuit files for common tesseract code operations. These files can be used independently with stim.
**An important note** is that the calculation of the Pauli frame is not included in these files, since it is achieved by classical computation done using Python code, outside of the Stim runtime. This means that running these circuits will not do the actual correction at the end. Check the Python code for the complete implementation.

## Generated Files

### 1. Encoding Circuits

- **`encoding_9a.stim`** - Encoding circuit for the |++0000⟩ state (Fig 9a)
  - 23 qubits total (16 data + 7 ancillas)
  - Prepares the tesseract code in the |++0000⟩ logical state

- **`encoding_9b.stim`** - Encoding circuit for the |+0+0+0⟩ state (Fig 9b) 
  - 18 qubits total (16 data + 2 ancillas)
  - Prepares the tesseract code in the |+0+0+0⟩ logical state

### 2. Error Correction

- **`error_correction_round.stim`** - Single round of error correction
  - 18 qubits total (16 data + 2 ancillas)
  - Measures stabilizers for both rows and columns
  - Includes flagged syndrome extraction

### 3. Decoding

- **`decoding.stim`** - Final measurement and decoding by diving to two [[8,3,2]] color codes
  - 18 qubits total (16 data + 2 ancillas)
  - Splits the tesseract code into two [[8,3,2]] color codes
  - Measures top half in X basis, bottom half in Z basis

### 4. Complete Experiments

- **`complete_experiment_9a.stim`** - Full experiment with 9a encoding
  - Encoding (9a) → 3 rounds of error correction → decoding
  - 23 qubits total

- **`complete_experiment_9b.stim`** - Full experiment with 9b encoding  
  - Encoding (9b) → 3 rounds of error correction → decoding
  - 18 qubits total

## Qubit Layout

All circuits use a consistent qubit layout:

```
Data qubits (0-15) arranged in 4×4 grid:
Row 1: 0  1  2  3   (y=0, x=0-3)
Row 2: 4  5  6  7   (y=1, x=0-3)  
Row 3: 8  9  10 11  (y=2, x=0-3)
Row 4: 12 13 14 15  (y=3, x=0-3)

Ancilla qubits: 16, 17, ... (at x=5, y=0,1,2,...)
```

## Usage Examples

### Using with stim directly

```bash
# Simulate the complete 9b experiment with 1000 shots
stim sample --shots 1000 --in complete_experiment_9a.stim
```

### Using in Python

```python
import stim

# Load a circuit
circuit = stim.Circuit.from_file("encoding_9a.stim")

# Run simulation
sampler = circuit.compile_sampler()
samples = sampler.sample(shots=1000)

# Get detector error model
dem = circuit.detector_error_model()
```

### Combining circuits

```python
import stim

# Load individual components
encoding = stim.Circuit.from_file("encoding_9a.stim")
ec_round = stim.Circuit.from_file("error_correction_round.stim")
decoding = stim.Circuit.from_file("decoding.stim")

# Combine into custom experiment
custom_circuit = stim.Circuit()
custom_circuit += encoding

# Add noise channel
custom_circuit.append("DEPOLARIZE1", range(16), 0.001)

# Add multiple EC rounds
for _ in range(5):  # 5 rounds instead of 3
    custom_circuit += ec_round

custom_circuit += decoding
```

## Generation

These files were generated using `generate_stim_files.py`, which uses the existing tesseract-code-stim Python implementation to build the circuits and export them to stim format.

To regenerate the files:

```bash
python stim_circuits/generate_stim_files.py
```

## Related Papers

- "Demonstration of quantum computation and error correction with a tesseract code" - http://arxiv.org/abs/2409.04628
- "The smallest interesting colour code" by Earl Campbell - https://earltcampbell.com/2016/09/26/the-smallest-interesting-colour-code/
