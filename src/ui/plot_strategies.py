from abc import ABC, abstractmethod

import numpy as np
from scipy.fft import fft, fftfreq, fftshift
from scipy import signal

import pyqtgraph as pg
from PySide6.QtCore import Qt,QRectF
from src.ui.plot_widgets import PlotWidget
from src.dataclasses.dataclass_models import PulseSignal, ModSchemeLUT, BasebandSignal
from src.constants import PulseShape


def downsample_for_plot(x_data, y_data, max_points=10000):
    """
    Intelligently downsample data for plotting to improve performance.
    Uses decimation for long signals while preserving visual appearance.

    Args:
        x_data: Time or frequency array
        y_data: Signal data (can be complex)
        max_points: Maximum number of points to plot (default 10k)

    Returns:
        Downsampled (x_data, y_data) tuple
    """
    if len(x_data) <= max_points:
        return x_data, y_data

    # Calculate decimation factor
    decimation_factor = len(x_data) // max_points

    # Decimate both arrays
    x_downsampled = x_data[::decimation_factor]
    y_downsampled = y_data[::decimation_factor]

    return x_downsampled, y_downsampled




class PlotStrategy(ABC):
    @abstractmethod
    def plot(self, widget: PlotWidget, signal_model):
        pass


class PulsePlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model: PulseSignal):
        widget.plot_widget.clear()

        # Time Vector Calculation in Seconds
        t_duration = len(signal_model.data) / signal_model.fs

        # Center the pulse around 0
        timevector_s = np.linspace(-t_duration/2, t_duration/2, len(signal_model.data))

        # CONVERSION TO MILLISECONDS (ms)
        timevector_ms = timevector_s * 1000

        widget.plot_widget.setTitle(f"Pulse: {signal_model.name}")

        # UPDATE UNIT LABEL TO MS
        widget.plot_widget.setLabel('bottom', 'Time', units='ms')

        # Downsample for performance
        time_ds, data_ds = downsample_for_plot(timevector_ms, signal_model.data, max_points=5000)

        # Plot with MS time vector
        widget.plot_data(time_ds, data_ds, color='b', name=signal_model.name)


class ConstellationPlotStrategy(PlotStrategy):
    """
    Plots the constellation diagram, including bit labels next to each symbol point.
    """

    def _design_plot(self, widget: PlotWidget, modscheme_signal_container: ModSchemeLUT):
        """
        Sets up the design and layout of the plot.
        """
        widget.plot_widget.clear()
        widget.plot_widget.setTitle(f"Constellation: {modscheme_signal_container.name}")
        widget.plot_widget.setLabel('bottom', 'In-Phase (I / Real)')
        widget.plot_widget.setLabel('left', 'Quadrature (Q / Imaginary)')
        widget.plot_widget.setAspectLocked(True)
        widget.plot_widget.showGrid(x=True, y=False)

        plot_item = widget.plot_widget.getPlotItem()

        cross_hair_pen = pg.mkPen('w', style=Qt.PenStyle.DashLine)
        plot_item.addLine(x = 0, pen = cross_hair_pen)
        plot_item.addLine(y = 0, pen = cross_hair_pen)

    def _process_data(self, modscheme_signal_container: ModSchemeLUT):
        """
        Processes the incoming data to prepare for plotting.
        """
        dict_look_up_table = modscheme_signal_container.look_up_table

        # Prepare data for plotting
        complex_symbols = np.array(list(dict_look_up_table.values()))
        i_data = complex_symbols.real
        q_data = complex_symbols.imag

        # Determine the number of bits per symbol (k) from the cardinality (M)
        M = len(dict_look_up_table)
        k = int(np.log2(M)) if M > 0 else 0

        # Define an offset for the label so it doesn't overlap the symbol point
        label_offset_i = 0.1 * np.max(np.abs(i_data)) if len(i_data) > 0 else 0.1
        label_offset_q = 0.1 * np.max(np.abs(q_data)) if len(q_data) > 0 else 0.1

        return dict_look_up_table, i_data, q_data, k, label_offset_i, label_offset_q

    def plot(self, widget: PlotWidget, modscheme_signal_container: ModSchemeLUT):
        """
        Combines design and data processing to plot the constellation diagram.
        """
        self._design_plot(widget, modscheme_signal_container)

        # Process data
        dict_look_up_table, i_data, q_data, k, label_offset_i, label_offset_q = self._process_data(modscheme_signal_container)

        # --- 1. Plot the Symbols ---
        scatter = pg.ScatterPlotItem(
            size=8,
            pen=pg.mkPen('w', width=1),
            brush=pg.mkBrush('b'),
            hoverable=True
        )
        scatter.addPoints(i_data, q_data)
        widget.plot_widget.addItem(scatter)

        # --- 2. Add Bit Labels (Annotation) ---

        # Determine the number of bits per symbol (k) from the cardinality (M)
        M = len(dict_look_up_table)
        k = int(np.log2(M)) if M > 0 else 0

        # Define an offset for the label so it doesn't overlap the symbol point
        label_offset_i = 0.1 * np.max(np.abs(i_data)) if len(i_data) > 0 else 0.1
        label_offset_q = 0.1 * np.max(np.abs(q_data)) if len(q_data) > 0 else 0.1

        # Iterate through the codebook to add labels
        for binary_index, symbol in dict_look_up_table.items():

            # Convert the key (0, 1, 2, 3...) to its corresponding bit sequence ('00', '01', '10', '11'...)
            bit_label = format(binary_index, f'0{k}b')

            # Create a pyqtgraph TextItem for the label
            # We add a small offset (label_offset_i) to position the text clearly
            text_item = pg.TextItem(
                text=bit_label,
                color=(255, 255, 255), # White text
                anchor=(0.5, 0)        # Anchor text center-bottom relative to the point
            )

            # Position the text slightly above the symbol point
            text_item.setPos(symbol.real + label_offset_i, symbol.imag + label_offset_q)

            widget.plot_widget.addItem(text_item)

        # Ensure the view bounds encompass all symbols and labels
        if len(i_data) > 0:
            max_val_i = np.max(np.abs(i_data)) * 1.4
            max_val_q = np.max(np.abs(q_data))
            widget.plot_widget.setXRange(-max_val_i, max_val_i, padding=0)
            widget.plot_widget.setYRange(-max_val_q, max_val_q, padding=0)

        widget.plot_widget.showGrid(x = True, y = False)


class BasebandPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model: BasebandSignal):
        widget.plot_widget.clear()

        num_samples = len(signal_model.data)

        timevector = np.arange(num_samples) / signal_model.fs

        real_component = np.real(signal_model.data)
        img_component = np.imag(signal_model.data)

        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Baseband Signal: {signal_model.name}")

        # Downsample for performance
        time_ds, real_ds = downsample_for_plot(timevector, real_component, max_points=10000)
        _, imag_ds = downsample_for_plot(timevector, img_component, max_points=10000)

        widget.plot_data(time_ds, real_ds, color='b', name=signal_model.name)
        widget.plot_data(time_ds, imag_ds, color='r', name=signal_model.name + " Imaginary", clear=False)


class BandpassPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model):

        widget.plot_widget.clear()

        num_samples = len(signal_model.data)

        timevector = np.arange(num_samples) / signal_model.fs

        real_component = np.real(signal_model.data)
        img_component = np.imag(signal_model.data)

        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Bandpass Signal: {signal_model.name}")

        # Downsample for performance
        time_ds, real_ds = downsample_for_plot(timevector, real_component, max_points=10000)
        _, imag_ds = downsample_for_plot(timevector, img_component, max_points=10000)

        widget.plot_data(time_ds, real_ds, color = 'b', name=signal_model.name)
        widget.plot_data(time_ds, imag_ds, color = 'r', name=signal_model.name + " Imaginary",clear=False)


class FFTPlotStrategy(PlotStrategy):
    def plot(self, widget, signal_model):
        data = signal_model.data
        fs = signal_model.fs

        # 1. Performance Guard: Decimate if oversampled (e.g., 48k for 10 Baud)
        if len(data) > 5000:
            factor = 100
            plot_data = signal.decimate(data, factor)
            plot_fs = fs / factor
        else:
            plot_data = data
            plot_fs = fs

        n = 2**12

        xk_complex = np.fft.fft(plot_data, n=n)
        xf = np.fft.fftfreq(n, d=1/plot_fs)

        # xk = (1/(fs*N)) * |fft(xn)|^2
        psd_raw = (1.0 / (plot_fs * n)) * np.abs(xk_complex)**2

        # Double values except for DC and Nyquist
        psd_raw[1:-1] *= 2

        # Convert to dB: pow2db(xk)
        psd_db = 10 * np.log10(psd_raw + 1e-12)

        # 4. Final Plotting
        widget.plot_widget.clear()
        widget.plot_widget.setLabel('left', 'Power Density', units='dB/Hz')
        widget.plot_data(xf, psd_db, color='b')


class PeriodogrammPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model):

        widget.plot_widget.clear()


        T_pulse = 1.0 / signal_model.sym_rate # Assuming symbol_rate is available

        # --- KEY CORRECTION: Use a large nfft for high frequency resolution ---
        nfft_size = 32768

        # 1. Calculate the Periodogram (One-sided, high-res)
        f, Pxx_den = signal.periodogram(signal_model.data,
                                        signal_model.fs,
                                        scaling='density',
                                        return_onesided=True,
                                        nfft=nfft_size)

        # 2. Convert PSD to dB/Hz (10 * log10(Power))
        Pxx_den_dB = 10 * np.log10(Pxx_den + 1e-10)

        # 3. Calculate Normalized Frequency (fT) for X-axis
        f_normalized = f * T_pulse

        # --- X-Range Centering ---
        # Find peak on the linear scale (Pxx_den)
        Pxx_den_idx_max = np.argmax(Pxx_den)
        index_x_normalized = f_normalized[Pxx_den_idx_max]

        # Since it's a normalized plot, set the range to show the first few lobes
        x_range_bottom = 0
        x_range_top = 2.5 # Extends to 2.5 times the symbol rate

        widget.plot_widget.setXRange(x_range_bottom, x_range_top)

        # --- Labels and Title ---
        widget.plot_widget.setLabel('bottom', 'Normalized Frequency ', units='fT')

        # *** Correct Label for dB plot ***
        widget.plot_widget.setLabel('left', 'Power Spectral Density', units='dB/Hz')

        widget.plot_widget.setTitle(f"High-Resolution Periodogram Spectrum")

        # --- Plotting ---
        widget.plot_data(f_normalized, Pxx_den_dB, color = 'b', name=signal_model.name)


class SpectogramPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model):

        NPERSEG = 256
        OVERLAP = NPERSEG // 2
        WINDOW_TYPE = 'hann'

        # 0. Type check/data preparation (Essential for robust code)
        if signal_model.data is np.iscomplexobj:
            data = np.real(signal_model.data)
        else:
            data = signal_model.data

        fs = signal_model.fs

        if fs <= 0 or len(data) == 0:
            widget.plot_widget.clear()
            widget.plot_widget.setTitle("Error: Invalid Sampling Rate or Empty Signal")
            return

        widget.plot_widget.clear()

        # 1. Compute the Spectrogram (Frequency, Time, Power Spectral Density)
        # We use the built-in convenience function for simplicity and robustness.
        f, t, Sxx = signal.spectrogram(
            data,
            fs=fs,
            window=WINDOW_TYPE,
            nperseg=NPERSEG,
            noverlap=OVERLAP,
            scaling='density'  # Use Power Spectral Density
        )

        # 2. Convert Power Spectral Density (Sxx) to dB scale (10 * log10(Sxx))
        # Add a small offset (1e-10) to avoid log(0) for truly zero values.
        # Transpose the array to ensure frequency (vertical) and time (horizontal)
        # axes match the pyqtgraph ImageItem orientation.
        spectrogram_db = 10 * np.log10(Sxx.T + 1e-10)

        # 3. Create the ImageItem and load the data
        img = pg.ImageItem()
        img.setImage(spectrogram_db)

        # 4. Set the position and scale of the image
        # This step is critical for aligning the spectrogram data matrix (spectrogram_db)
        # with the axes coordinates (t and f).
        time_span = t[-1] - t[0]
        freq_span = f[-1] - f[0]

        img.setRect(QRectF(
            t[0],     # x_min (start time)
            f[0],     # y_min (start frequency)
            time_span, # x_span (total duration)
            freq_span * 0.00001  # y_span (total frequency range)
        ))

        # 5. Add the image to the plot
        widget.plot_widget.addItem(img)

        # 6. Configure Axes and Title
        widget.plot_widget.setLabel('bottom', 'Time ', units='s')
        widget.plot_widget.setLabel('left', 'Frequency', units='Hz')
        widget.plot_widget.setTitle(f"Spectrogram (Nseg={256}, {WINDOW_TYPE.upper()} Window)")

        # Optional: Auto-range the view to fit the spectrogram
        widget.plot_widget.getViewBox().autoRange()

class FrequencyResponse(PlotStrategy):
    def plot(self, widget, signal_model):

        n_fft = 2 ** 8
        h = np.fft.rfft(signal_model.data, n = n_fft)
        xf_hz = np.fft.rfftfreq(n_fft, d=1/signal_model.fs)

        mag_db = 20 * np.log10(np.abs(h) + 1e-12)

        # 3. Theoretical Group Delay (Constant for symmetric FIR)
        # Avoids the 1e19 numerical artifacts

        widget.plot_widget.setTitle(f"FIR Analysis: {signal_model.name}")
        widget.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        widget.plot_widget.setLabel('left', 'Magnitude', units='dB')
        widget.plot_widget.setXRange(0, signal_model.fs / 2)

        widget.plot_data(xf_hz, mag_db)




class PlotManager:
    def __init__(self, widget: PlotWidget):
        self.widget = widget
        self.strategy = None

    def set_strategy(self, strategy: PlotStrategy):
        self.strategy = strategy

    def update_plot(self, signal_model):
        if self.strategy:
            self.strategy.plot(self.widget, signal_model)

    def clear_plot(self):
        self.widget.plot_widget.clear()



# TODO Handle Complex Data in Plotstrategies