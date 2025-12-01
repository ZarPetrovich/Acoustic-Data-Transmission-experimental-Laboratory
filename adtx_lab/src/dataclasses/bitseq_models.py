from dataclasses import dataclass
from typing import Dict
import numpy as np

@dataclass
class SymbolSequence:
    """
    SymbolSequence is a data class that represents a sequence of symbols with associated metadata.

    Attributes:
        name (str): The name of the symbol sequence.
        data (np.ndarray): The array containing the symbol data.
        look_up_table (np.ndarray): A lookup table associated with the symbol sequence.
        length (int, optional): The length of the symbol sequence. Automatically calculated based on `data` if not provided.
        mod_scheme (str, optional): The modulation scheme associated with the symbol sequence.

    Methods:
        __post_init__(): A post-initialization method that calculates the length of the `data` array if it is not None.
    """
    def __post_init__(self):
        if self.data is not None:
            self.length = len(self.data)
    name: str
    data: np.ndarray
    look_up_table: Dict[int, complex]
    length: int = None,
    mod_scheme: str = None






