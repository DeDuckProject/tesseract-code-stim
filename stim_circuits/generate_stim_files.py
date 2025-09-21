#!/usr/bin/env python3
"""
Script to generate stim circuit files for common tesseract code circuits.
This script uses the existing circuit building functions from run.py to generate
.stim files that can be used independently.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tesseract_sim.run import build_encoding_circuit, build_error_correction_circuit
from tesseract_sim.common.circuit_base import init_circuit
from tesseract_sim.encoding.encoding_manual_9a import encode_manual_fig9a
from tesseract_sim.encoding.encoding_manual_9b import encode_manual_fig9b
from tesseract_sim.error_correction.measurement_rounds import (
    error_correction_round_rows, 
    error_correction_round_columns,
    measure_logical_operators_tesseract
)
from tesseract_sim.noise.noise_cfg import NO_NOISE


def generate_encoding_9a_stim():
    """Generate stim file for encoding 9a (|++0000> state)"""
    circuit = init_circuit(qubits=16, ancillas=7)  # Need extra ancillas for encoding 9a
    encode_manual_fig9a(circuit, cfg=NO_NOISE)
    return circuit


def generate_encoding_9b_stim():
    """Generate stim file for encoding 9b (|+0+0+0> state)"""
    circuit = init_circuit(qubits=16, ancillas=2)
    encode_manual_fig9b(circuit, cfg=NO_NOISE)
    return circuit


def generate_error_correction_round_stim():
    """Generate stim file for 1 error correction round (rows + columns)"""
    circuit = init_circuit(qubits=16, ancillas=2)
    error_correction_round_rows(circuit, cfg=NO_NOISE)
    error_correction_round_columns(circuit, cfg=NO_NOISE)
    circuit.append_operation("TICK")
    return circuit


def generate_decoding_stim():
    """Generate stim file for decoding with two [[8,3,2]] color codes + measurement"""
    circuit = init_circuit(qubits=16, ancillas=2)
    measure_logical_operators_tesseract(circuit, cfg=NO_NOISE)
    return circuit


def generate_complete_experiment_9a_stim():
    """Generate stim file for complete experiment with 9a encoding"""
    circuit = init_circuit(qubits=16, ancillas=7)
    
    # Add encoding comment
    circuit.append("TICK")
    circuit.append_operation("# Start encoding based on Fig. 9a", [])
    
    # Encoding 9a
    encode_manual_fig9a(circuit, cfg=NO_NOISE)
    
    # 3 rounds of error correction
    for i in range(3):
        circuit.append_operation("# Start EC round {}".format(i+1), [])
        error_correction_round_rows(circuit, cfg=NO_NOISE)
        error_correction_round_columns(circuit, cfg=NO_NOISE)
        circuit.append_operation("TICK")
    
    # Final measurements
    circuit.append_operation("# Start decoding", [])
    measure_logical_operators_tesseract(circuit, cfg=NO_NOISE)
    
    return circuit


def generate_complete_experiment_9b_stim():
    """Generate stim file for complete experiment with 9b encoding"""
    circuit = init_circuit(qubits=16, ancillas=2)
    
    # Encoding 9b
    encode_manual_fig9b(circuit, cfg=NO_NOISE)
    
    # 3 rounds of error correction
    for i in range(3):
        error_correction_round_rows(circuit, cfg=NO_NOISE)
        error_correction_round_columns(circuit, cfg=NO_NOISE)
        circuit.append_operation("TICK")
    
    # Final measurements
    measure_logical_operators_tesseract(circuit, cfg=NO_NOISE)
    
    return circuit


def save_stim_file(circuit, filename, description):
    """Save a stim circuit to a file with header comments"""
    stim_str = str(circuit)
    
    # Add header comments
    header = f"""# {description}
# Generated from tesseract-code-stim project
# Circuit has {circuit.num_qubits} qubits total
# 
# Qubit layout:
# - Qubits 0-15: Data qubits arranged in 4x4 grid
# - Qubits 16+: Ancilla qubits for measurements
#
# Coordinate system:
# - Qubits 0-3: row 1 (y=0, x=0-3)
# - Qubits 4-7: row 2 (y=1, x=0-3) 
# - Qubits 8-11: row 3 (y=2, x=0-3)
# - Qubits 12-15: row 4 (y=3, x=0-3)
#

"""
    
    with open(filename, 'w') as f:
        f.write(header)
        f.write(stim_str)
    
    print(f"Generated {filename} - {description}")


def main():
    """Generate all stim circuit files"""
    os.makedirs('stim_circuits', exist_ok=True)
    
    circuits = [
        (generate_encoding_9a_stim(), 'stim_circuits/encoding_9a.stim', 'Encoding 9a circuit (|++0000> state)'),
        (generate_encoding_9b_stim(), 'stim_circuits/encoding_9b.stim', 'Encoding 9b circuit (|+0+0+0> state)'),
        (generate_error_correction_round_stim(), 'stim_circuits/error_correction_round.stim', 'Single error correction round (rows + columns)'),
        (generate_decoding_stim(), 'stim_circuits/decoding.stim', 'Decoding with two [[8,3,2]] color codes + measurement'),
        (generate_complete_experiment_9a_stim(), 'stim_circuits/complete_experiment_9a.stim', 'Complete experiment: encoding 9a -> 3 EC rounds -> decoding'),
        (generate_complete_experiment_9b_stim(), 'stim_circuits/complete_experiment_9b.stim', 'Complete experiment: encoding 9b -> 3 EC rounds -> decoding'),
    ]
    
    for circuit, filename, description in circuits:
        save_stim_file(circuit, filename, description)
    
    print(f"\nAll stim files generated successfully!")
    print("Files created:")
    for _, filename, _ in circuits:
        print(f"  - {filename}")


if __name__ == "__main__":
    main()
