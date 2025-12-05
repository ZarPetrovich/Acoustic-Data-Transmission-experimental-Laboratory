"""
Dataclass Container to store Data + Metadata through
different types of Signals inside the application.

Can also be used to export the data

"""

from dataclasses import dataclass, field
from typing import Dict
import numpy as np
from adtx_lab.src.constants import PulseShape, ModulationScheme

# ===========================================================
#  Dataclass Container
#   1. Bit/Symbol Sequences     @@@SequenceContainer
#   2. Time Domain Signals      @@@SignalContainer
# ===========================================================

#------------------------------------------------------------
# +++++ PARENT CONTAINER +++++
#------------------------------------------------------------

@dataclass
class DataContainer:
    name: str
    data: np.ndarray

#------------------------------------------------------------
# +++++ @@@SequenceContainer +++++
#------------------------------------------------------------

@dataclass
class ModSchemeLUT(DataContainer):
    """
    ModschemeLUT is a data class that represents a Look up Table for a
    specific Modulation Scheme with associated metadata.
    """
    look_up_table: Dict[int, complex]
    cardinality: int
    mapper: str
    mod_scheme: ModulationScheme

@dataclass
class StreamContainer(DataContainer):
    length: int = field(init=False)

    def __post_init__(self):
        if self.data is not None:
            self.length = len(self.data)
        else:
            self.length = 0

@dataclass
class BitStream(StreamContainer):
    ...

@dataclass
class SymbolStream(StreamContainer):
    mod_scheme: ModSchemeLUT
    bit_stream: BitStream






#------------------------------------------------------------
# +++++ @@@SignalContainer +++++
#------------------------------------------------------------

@dataclass
class SignalContainer(DataContainer):
    fs: int
    sym_rate: int

@dataclass
class PulseSignal(SignalContainer):
    """Data Container for created Pulses"""
    shape: PulseShape
    span: int = None

@dataclass
class BasebandSignal(SignalContainer):
    """Represents a modulated baseband signal.
    Reflect a compostion of:
        - Pulse Signal
        - Bit Sequence
        """
    pulse: PulseSignal
    symbol_stream: SymbolStream

