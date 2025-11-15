from dataclasses import dataclass
import numpy as np

@dataclass
class BitSequence:
    """The base class for all signal types in the application."""
    name: str
    data: np.ndarray
    data_rate: float = None



