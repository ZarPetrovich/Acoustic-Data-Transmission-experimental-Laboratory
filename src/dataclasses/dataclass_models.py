"""
Dataclass Container to store Data + Metadata through
different types of Signals inside the application.

Can also be used to export the data

"""

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Dict
import numpy as np
from src.constants import PulseShape, ModulationScheme, BitMappingScheme

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
class SignalContext:
    name: str
    data: np.ndarray

#------------------------------------------------------------
# +++++ @@@SequenceContainer +++++
#------------------------------------------------------------

@dataclass_json
@dataclass
class ModulationModel(SignalContext):
    """Represents the mathematical state of the modulation stage."""
    look_up_table: Dict[int, complex]
    cardinality: int
    mapper: BitMappingScheme
    mod_scheme: ModulationScheme

@dataclass_json
@dataclass
class StreamContainer(SignalContext):
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
    mod_scheme: ModulationModel
    bit_stream: BitStream


#------------------------------------------------------------
# +++++ @@@SignalContainer +++++
#------------------------------------------------------------

@dataclass_json
@dataclass
class SignalModelContainer(SignalContext):
    fs: int
    sym_rate: int

@dataclass_json
@dataclass
class PulseModel(SignalModelContainer):
    """Data Container for created Pulses"""
    shape: str
    span: int = None
    roll_off: float = None

@dataclass_json
@dataclass
class BasebandModel(SignalModelContainer):
    """Represents a modulated baseband signal.
    Reflect a compostion of:
        - Pulse Signal
        - Bit Sequence
        """
    pulse: PulseModel
    symbol_stream: SymbolStream

@dataclass_json
@dataclass
class BandpassModel(SignalModelContainer):
    baseband_signal: BasebandModel
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
    scheme_enum: ModulationScheme
    cardinality: int
    mapper_enum: BitMappingScheme
    display_name: str

@dataclass
class BitstreamUpdateTask:
    bit_stream: str

@dataclass
class CarrierUpdateTask:
    """DTO for UI-to-Logic communication regarding the carrier."""
    carrier_freq: int