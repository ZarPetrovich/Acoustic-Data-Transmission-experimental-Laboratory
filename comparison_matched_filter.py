import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Parameters
fs = 4000
sps = 100
bits = np.array([0, 1, 0, 1, 1])
symbols = 2 * bits - 1 # Polar NRZ

# Impulse train
impulse_train = np.zeros(len(symbols) * sps)
impulse_train[::sps] = symbols

# 1. Rectangle
rect_pulse = np.ones(sps)

# 2. Gaussian (Fixed for newer SciPy)
# std is the standard deviation in samples
gaussian_pulse = signal.windows.gaussian(sps, std=sps/6)

# 3. Raised Cosine (Standard implementation)
t_rc = np.linspace(-sps/2, sps/2, sps)
alpha = 0.5
# Sinc * Cosine part
with np.errstate(divide='ignore', invalid='ignore'):
    rc_pulse = np.sinc(t_rc/sps) * np.cos(np.pi*alpha*t_rc/sps) / (1 - (2*alpha*t_rc/sps)**2)
    rc_pulse[np.isnan(rc_pulse)] = np.max(rc_pulse) # Handle division by zero

pulses = [("Rectangle", rect_pulse), ("Gaussian", gaussian_pulse), ("Raised Cosine", rc_pulse)]

fig, axes = plt.subplots(3, 2, figsize=(12, 10), constrained_layout=True)

for i, (name, pulse) in enumerate(pulses):
    # Normalize
    pulse = pulse / np.sum(np.abs(pulse))

    # TX Waveform
    tx_signal = np.convolve(impulse_train, pulse, mode='full')

    # Matched Filter Output
    # The 'Dump' point is at the end of the first pulse duration
    mf_output = np.convolve(tx_signal, pulse[::-1], mode='full')

    # Plotting TX
    axes[i, 0].plot(tx_signal[:sps*5], color='tab:blue', lw=2)
    axes[i, 0].set_title(f"{name} Pulse: Transmitted (Baseband)")
    axes[i, 0].grid(True, alpha=0.3)

    # Plotting MF Output (The Decisions)
    axes[i, 1].plot(mf_output[:sps*5], color='tab:orange', lw=2)
    axes[i, 1].set_title(f"{name} Pulse: Matched Filter (Peaks)")

    # Mark the optimal sampling points (The "Dump" moments)
    # The first peak occurs at sps-1 due to convolution delay
    sample_indices = np.arange(sps - 1, sps * 5, sps)
    axes[i, 1].plot(sample_indices, mf_output[sample_indices], 'ro', label='Sampling Points')
    axes[i, 1].grid(True, alpha=0.3)

plt.show()