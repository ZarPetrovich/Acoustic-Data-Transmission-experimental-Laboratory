from abc import ABC, abstractmethod
import numpy as np

from adtx_lab.src.dataclasses.bitseq_models import BitSequence

class NRZMapper(ABC):

    @abstractmethod
    def generate(self, bit_seq: np.ndarray) -> np.ndarray:
        pass


class PolarNRZMapping(NRZMapper):

    def generate(self, bit_seq: np.ndarray) -> np.ndarray:
        return 2 * bit_seq.astype(float) - 1


class UniPolarNRZMapping(NRZMapper):

    def generate(self, bit_seq: np.ndarray) -> np.ndarray:
        return bit_seq.astype(float)


if __name__ == "__main__":
    bit_seq = np.array([1, 0, 1, 1, 0, 0, 1])

    raw_bit_seq = BitSequence("Raw Bit Seq",
                              bit_seq,
                              data_rate=1,
                              )

    # Init the Mapper and store than as Objects
    polar_mapper = PolarNRZMapping()
    unipolar_mapper = UniPolarNRZMapping()

    # use the Objects to really generate the mapped symbols
    polar_symbols = BitSequence("Polar Mapped Seq",
                                polar_mapper.generate(raw_bit_seq.data),
                                data_rate=1,
                                )

    print(f"Polar: {polar_symbols}")
