from enum import Enum, auto

class PulseShape(Enum):
    """Defines the available pulse shapes as unique constants."""
    RECTANGLE = auto()
    COSINE_SQUARED = auto()

class BitMappingScheme(Enum):
    """Defines the available bit mapping schemes as unique constants"""
    POLARNRZMAPPING = auto()
    UNIPOLARNRZMAPPING = auto()

class ModulationScheme(Enum):
    """Defines the available modulation schemes as unique constants."""
    AMPLITUDE_MODULATION = auto()

    AMPLITUDE_SHIFT_KEYING = auto()
    ASK = AMPLITUDE_SHIFT_KEYING

    PHASE_SHIFT_KEYING = auto()
    PSK = PHASE_SHIFT_KEYING

