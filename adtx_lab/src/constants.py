from enum import Enum, auto

class PulseShape(Enum):
    """Defines the available pulse shapes as unique constants."""
    RECTANGLE = auto()
    COSINE_SQUARED = auto()
    RAISED_COSINE = auto()

class BitMappingScheme(Enum):
    """Defines the available bit mapping schemes."""
    GRAY = auto()
    BINARY = auto()
    RANDOM = auto()

class ModulationScheme(Enum):
    """Defines the available modulation schemes as unique constants."""

    AMPLITUDE_SHIFT_KEYING = auto()
    ASK = AMPLITUDE_SHIFT_KEYING

    PHASE_SHIFT_KEYING = auto()
    PSK = PHASE_SHIFT_KEYING

# Default Application Settings
DEFAULT_FS = 48000
DEFAULT_SYM_RATE = 100

# UI Mappings
PULSE_SHAPE_MAP = {
    PulseShape.RECTANGLE: "Rectangle",
    PulseShape.COSINE_SQUARED: "Cosine",
}

AVAILABLE_FS = [44100, 48000]

