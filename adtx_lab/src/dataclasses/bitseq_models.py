from dataclasses import dataclass
import numpy as np

@dataclass
class SymbolSequence:

    def __post_init__(self):
        if self.data is not None:
            self.length = len(self.data)
    name: str
    data: np.ndarray
    length: int = None
    sym_rate: float = None
    data_rate: float = None
    length: int
    mod_scheme: str = None






