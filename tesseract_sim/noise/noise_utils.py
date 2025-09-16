import stim
from typing import Sequence, Literal
from .noise_cfg import NoiseCfg, NO_NOISE

CURRENT_NOISE_CFG: NoiseCfg = NO_NOISE

def append_op(
    circuit: stim.Circuit,
    opname: str,
    targets: Sequence[int],
    phase: Literal['enc', 'ec', 'meas'],
    cfg: NoiseCfg = CURRENT_NOISE_CFG
):
    circuit.append(opname, targets)
    
    active_noise = False
    rate_1q = 0.0
    rate_2q = 0.0
    op1 = cfg.op1
    op2 = cfg.op2

    if phase == 'enc' and cfg.enc_active:
        active_noise = True
        rate_1q = cfg.enc_rate_1q
        rate_2q = cfg.enc_rate_2q
    elif phase == 'ec' and cfg.ec_active:
        active_noise = True
        rate_1q = cfg.ec_rate_1q
        rate_2q = cfg.ec_rate_2q
    elif phase == 'meas' and cfg.meas_active:
        active_noise = True
        rate_1q = cfg.meas_error_rate
        rate_2q = cfg.meas_error_rate  # Use same rate for consistency

    if active_noise:
        if len(targets) == 1 and rate_1q > 0:
            circuit.append(op1, targets, rate_1q)
        elif len(targets) > 1 and rate_2q > 0:
            circuit.append(op2, targets, rate_2q)

def append_1q(circuit: stim.Circuit, opname: str, target: int, phase: Literal['enc', 'ec', 'meas'], cfg: NoiseCfg = CURRENT_NOISE_CFG):
    append_op(circuit, opname, [target], phase, cfg)

def append_2q(circuit: stim.Circuit, opname: str, target1: int, target2: int, phase: Literal['enc', 'ec', 'meas'], cfg: NoiseCfg = CURRENT_NOISE_CFG):
    append_op(circuit, opname, [target1, target2], phase, cfg) 