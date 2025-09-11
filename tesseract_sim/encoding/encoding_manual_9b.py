from tesseract_sim.noise.noise_cfg import NoiseCfg, NO_NOISE
from tesseract_sim.noise.noise_utils import append_1q, append_2q


def encode_000_in_8_3_2_color_code(circuit, participating_qubits: list[int], ancillas: list[int], cfg: NoiseCfg = NO_NOISE):
    """Encodes |000> state in an [[8,3,2]] color code as shown in Fig 9b.

    see:
    E. Campbell, "The smallest interesting colour code," Online available at https://earltcampbell.com/2016/09/26/the-smallest-interesting-colour-code/ (2016), accessed on 2019-12-09.
    https://errorcorrectionzoo.org/c/stab_8_3_2
    
    Args:
        circuit: The circuit to append operations to
        participating_qubits: List of 8 qubits to encode
        ancillas: List of 2 ancilla qubits [z_ancilla, x_ancilla]
        cfg: Noise configuration to use
    """

    z_ancilla = ancillas[0]
    x_ancilla = ancillas[1]

    # Initialize states:
    append_1q(circuit, "H", x_ancilla, phase="enc", cfg=cfg)
    for i in [participating_qubits[0], participating_qubits[3], participating_qubits[6], participating_qubits[7]]:
        append_1q(circuit, "H", i, phase="enc", cfg=cfg)

    # cnot operations as described in Fig 9b, from top to bottom, left to right:
    append_2q(circuit, "CNOT", participating_qubits[0], participating_qubits[1], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[6], participating_qubits[2], phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", participating_qubits[0], participating_qubits[4], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[6], participating_qubits[5], phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", participating_qubits[0], participating_qubits[5], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[6], participating_qubits[1], phase="enc", cfg=cfg)


    append_2q(circuit, "CNOT", participating_qubits[3], participating_qubits[2], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[7], participating_qubits[4], phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", participating_qubits[3], participating_qubits[4], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[7], participating_qubits[1], phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", participating_qubits[3], participating_qubits[5], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[7], participating_qubits[2], phase="enc", cfg=cfg)

    # for measuring stabilizers:
    append_2q(circuit, "CNOT", x_ancilla, participating_qubits[0], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[1], z_ancilla, phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", x_ancilla, participating_qubits[1], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[0], z_ancilla, phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", x_ancilla, participating_qubits[2], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[3], z_ancilla, phase="enc", cfg=cfg)

    append_2q(circuit, "CNOT", x_ancilla, participating_qubits[3], phase="enc", cfg=cfg)
    append_2q(circuit, "CNOT", participating_qubits[2], z_ancilla, phase="enc", cfg=cfg)

    # finally change X ancilla to computational basis
    append_1q(circuit, "H", x_ancilla, phase="enc", cfg=cfg)

    # Measure ancilla qubits
    append_1q(circuit, "M", x_ancilla, phase="enc", cfg=cfg)
    append_1q(circuit, "M", z_ancilla, phase="enc", cfg=cfg)


def encode_manual_fig9b(circuit, cfg: NoiseCfg = NO_NOISE):
    """Encodes |+0+0+0> state according to Fig 9b by running the 8-qubit encoding twice.
    First on rows 1,2 (qubits 0-7) and then on rows 3,4 (qubits 8-15).
    
    The first block is prepared in logical |+++> state by applying transversal Hadamards
    after encoding |000>. The second block stays in logical |000> state."""

    # Encode first block (rows 1,2, qubits 0-7) in |000> state first
    encode_000_in_8_3_2_color_code(circuit, participating_qubits=[0, 1, 2, 3, 4, 5, 6, 7], ancillas=[16, 17], cfg=cfg)
    
    # Apply transversal Hadamards to first block to convert |000> to |+++>
    # This ensures X measurements on the top half give deterministic results
    for i in range(8):
        append_1q(circuit, "H", i, phase="enc", cfg=cfg)
    
    # Encode second block (rows 3,4, qubits 8-15) in |000> state (stays as |000>)
    encode_000_in_8_3_2_color_code(circuit, participating_qubits=[8, 9, 10, 11, 12, 13, 14, 15], ancillas=[16, 17], cfg=cfg)

    circuit.append_operation("TICK")
