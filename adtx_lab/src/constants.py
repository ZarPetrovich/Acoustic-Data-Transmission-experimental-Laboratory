"""
 This module defines constants and enumerations used throughout the application
 Classes:
     PulseShape (Enum): Defines the available pulse shapes as unique constants.
         - RECTANGLE: Represents a rectangular pulse shape.
         - COSINE_SQUARED: Represents a cosine-squared pulse shape.
         - RAISED_COSINE: Represents a raised cosine pulse shape.
     BitMappingScheme (Enum): Defines the available bit mapping schemes.
         - GRAY: Represents Gray coding.
         - BINARY: Represents binary coding.
         - RANDOM: Represents random bit mapping.
     ModulationScheme (Enum): Defines the available modulation schemes as unique constants.
         - AMPLITUDE_SHIFT_KEYING: Represents amplitude shift keying (ASK).
         - PHASE_SHIFT_KEYING: Represents phase shift keying (PSK).
         - ASK: Alias for AMPLITUDE_SHIFT_KEYING.
         - PSK: Alias for PHASE_SHIFT_KEYING
 Constants:
     PULSE_SHAPE_MAP (dict): Maps PulseShape enum values to their string representations for UI purposes.
         - RECTANGLE: "Rectangle"
         - COSINE_SQUARED: "Cosine"
     DEFAULT_FS (int): The default sampling frequency (in Hz) used in the application.
     DEFAULT_SYM_RATE (int): The default symbol rate used in the application.
     AVAILABLE_FS (list): A list of available sampling frequencies (in Hz) supported by the application.
"""

from enum import Enum, auto

# ===========================================================
#   ENUM / MAP
#   1. Pulse + Map
#   2. Bitmapping Schemes
#   3. Modulation Schemes
# ===========================================================


class PulseShape(Enum):
    """Defines the available pulse shapes as unique constants."""
    RECTANGLE = auto()
    COSINE_SQUARED = auto()
    RAISED_COSINE = auto()

# UI Mappings
PULSE_SHAPE_MAP = {
    PulseShape.RECTANGLE: "Rectangle",
    PulseShape.COSINE_SQUARED: "Cosine",
}
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


# ===========================================================
#   App Start-Up Parameters
# ===========================================================

DEFAULT_FS = 48000
DEFAULT_SYM_RATE = 100

AVAILABLE_FS = [44100, 48000]

