from enum import Enum, auto

class PulseShape(Enum):
    """Defines the available pulse shapes as unique constants."""
    RECTANGLE = auto()
    COSINE_SQUARED = auto()



class ModulationScheme(Enum):
    """Defines the available modulation schemes as unique constants."""
    AMPLITUDE_MODULATION = auto()
