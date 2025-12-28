"""
Dataclass Container to store Data + Metadata through
different types of Signals inside the application.

Can also be used to export the data

"""

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict
import numpy as np
from src.constants import PulseShape, ModulationScheme

# ===========================================================
#  Dataclass Container
#   1. Bit/Symbol Sequences     @@@SequenceContainer
#   2. Time Domain Signals      @@@SignalContainer
# ===========================================================

#------------------------------------------------------------
# +++++ PARENT CONTAINER +++++
#------------------------------------------------------------
@dataclass_json
@dataclass
class DataContainer:
    name: str
    data: np.ndarray

#------------------------------------------------------------
# +++++ @@@SequenceContainer +++++
#------------------------------------------------------------
@dataclass_json
@dataclass
class ModSchemeLUT(DataContainer):
    """
    ModschemeLUT is a data class that represents a Look up Table for a
    specific Modulation Scheme with associated metadata.
    """
    look_up_table: Dict[int, complex]
    cardinality: int
    mapper: str
    mod_scheme: str
@dataclass_json
@dataclass
class StreamContainer(DataContainer):
    length: int = field(init=False)

    def __post_init__(self):
        if self.data is not None:
            self.length = len(self.data)
        else:
            self.length = 0
@dataclass_json
@dataclass
class BitStream(StreamContainer):
    ...
@dataclass_json
@dataclass
class SymbolStream(StreamContainer):
    mod_scheme: ModSchemeLUT
    bit_stream: BitStream


#------------------------------------------------------------
# +++++ @@@SignalContainer +++++
#------------------------------------------------------------

@dataclass_json
@dataclass
class SignalContainer(DataContainer):
    fs: int
    sym_rate: int
@dataclass_json
@dataclass
class PulseSignal(SignalContainer):
    """Data Container for created Pulses"""
    shape: str
    span: int = None
    roll_off: float = None
@dataclass_json
@dataclass
class BasebandSignal(SignalContainer):
    """Represents a modulated baseband signal.
    Reflect a compostion of:
        - Pulse Signal
        - Bit Sequence
        """
    pulse: PulseSignal
    symbol_stream: SymbolStream
@dataclass_json
@dataclass
class BandpassSignal(SignalContainer):
    baseband_signal: BasebandSignal
    carrier_freq: int


# ===========================================================
#   DTO - Data Transfer Object
# ===========================================================

@dataclass
class PulseUpdateTask:
    """The Transfer Class: Only data the UI actually knows."""
    shape_name: str
    span: int
    roll_off: float

@dataclass
class ModSchemeUpdateTask:
    mod_scheme: str
    bit_mapping: str

@dataclass
class BitstreamUpdateTask:
    bit_stream: str

@dataclass
class CarrierUpdateTask:
    """DTO for UI-to-Logic communication regarding the carrier."""
    carrier_freq: int