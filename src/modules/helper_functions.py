import json
import numpy as np
from scipy.io import wavfile
from pathlib import Path
from src.dataclasses.dataclass_models import BandpassModel, BitStreamModel


# ===========================================================
#   HELPER FUNCTIONS
# ===========================================================


def export_transmitted_signal(signal: BandpassModel, filename, filepath):
    """
    Export a signal as a WAV file.

    Parameters:
    filename (str): The name of the output WAV file.
    signal (np.ndarray): The audio signal data.
    fs (int): The sampling frequency.
    """
    # Normalize signal to the range of int16

    full_path = Path(filepath) / filename
    data = signal.data
    fs = signal.baseband_signal.fs
    normalized_signal = np.int16((data / np.max(np.abs(data))) * 32767)

    try:
        wavfile.write(str(full_path), fs, normalized_signal)

    except Exception as e:
        print(f"Error during WAV file export: {e}")

    metadata = {
        "name": filename,
        "fs": fs,
        "sym_rate": signal.baseband_signal.sym_rate,
        "carrier_freq": signal.carrier_freq,
        "pulse": {
            "shape": signal.baseband_signal.pulse.shape,
            "span": signal.baseband_signal.pulse.span,
            "roll_off": signal.baseband_signal.pulse.roll_off
        },
        "modulation_scheme": signal.baseband_signal.symbol_stream.mod_scheme.mod_scheme
    }

    try:

        data = json.dumps([
            {k: metadata[k] for k in metadata}],
            indent=4,
            )

        with open(full_path.with_suffix('.json'), 'w') as json_file:
            json_file.write(data)

    except TypeError as e:
        print(f"Error during WAV file export: {e}")



def add_barker_code(bitstream: BitStreamModel):
    barker_bits = np.array([1,1,1,0,0,1,0])

    bitstream = np.concatenate((barker_bits,bitstream.data))

    return bitstream