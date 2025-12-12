import numpy as np
from scipy.io import wavfile
from pathlib import Path
from src.dataclasses.dataclass_models import BandpassSignal


# ===========================================================
#   HELPER FUNCTIONS
# ===========================================================


def export_wav(signal: BandpassSignal, filename, filepath):
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