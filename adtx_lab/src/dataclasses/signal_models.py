from dataclasses import dataclass
import numpy as np
from adtx_lab.src.constants import PulseShape, ModulationScheme

@dataclass
class BaseSignal:
    """The base class for all signal types in the application."""
    name: str
    data: np.ndarray
    fs: int
    sym_rate: int

@dataclass
class PulseSignal(BaseSignal):
    """Represents a generated pulse shape."""
    shape: PulseShape
    span: int = None

@dataclass
class BasebandSignal(BaseSignal):
    """Represents a modulated baseband signal."""
    pulse_name: str
    bit_seq_name: str

@dataclass
class BandpassSignal(BaseSignal):
    """Represents a bandpass modulated signal."""
    pulse_name: str
    bit_seq_name: str
    baseband_name: str
    mod_scheme: ModulationScheme