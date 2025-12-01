from dataclasses import dataclass, field
from typing import Dict, Any
import numpy as np
from adtx_lab.src.constants import PulseShape

@dataclass
class SymbolSequence:
    """
    SymbolSequence is a data class that represents a sequence of symbols with associated metadata.
    """
    name: str
    data: np.ndarray
    look_up_table: Dict[int, complex]
    mod_scheme: str = None
    length: int = field(init=False)

    def __post_init__(self):
        if self.data is not None:
            self.length = len(self.data)
        else:
            self.length = 0

@dataclass
class PulseSignal:
    """Represents a generated pulse shape."""
    name: str
    data: np.ndarray
    fs: int
    sym_rate: int
    shape: PulseShape
    span: int = None

@dataclass
class BasebandSignal:
    """Represents a modulated baseband signal."""
    name: str
    data: np.ndarray
    fs: int
    sym_rate: int
    pulse_name: str
    bit_seq: str
    sym_name: str
