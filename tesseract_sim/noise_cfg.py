from dataclasses import dataclass, field
from typing import Literal

@dataclass
class NoiseCfg:
    enc_active: bool = False           # apply to encoding?
    enc_rate_1q: float = 0.0
    enc_rate_2q: float = 0.0
    ec_active: bool  = False           # apply to error-corr. rounds?
    ec_rate_1q: float = 0.0
    ec_rate_2q: float = 0.0
    op1: str = "DEPOLARIZE1"
    op2: str = "DEPOLARIZE2"

# TODO add noise on 'meas' phase as well

NO_NOISE = NoiseCfg() 