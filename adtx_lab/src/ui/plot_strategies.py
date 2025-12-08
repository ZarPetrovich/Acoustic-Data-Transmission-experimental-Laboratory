from abc import ABC, abstractmethod

import numpy as np
from scipy.fft import fft, fftfreq
from scipy import signal

import pyqtgraph as pg
from PySide6.QtCore import Qt
from adtx_lab.src.ui.plot_widgets import PlotWidget
from adtx_lab.src.dataclasses.dataclass_models import PulseSignal, ModSchemeLUT, BasebandSignal
from adtx_lab.src.constants import PulseShape




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

        # Plot with MS time vector
        widget.plot_data(timevector_ms, signal_model.data, color='b', name=signal_model.name)


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

        widget.plot_data(timevector, real_component, color = 'b', name=signal_model.name)
        widget.plot_data(timevector, img_component, color = 'r', name=signal_model.name + " Imaginary",clear=False)

class BandpassPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model):

        widget.plot_widget.clear()

        num_samples = len(signal_model.data)

        timevector = np.arange(num_samples) / signal_model.fs

        real_component = np.real(signal_model.data)
        img_component = np.imag(signal_model.data)

        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Baseband Signal: {signal_model.name}")

        widget.plot_data(timevector, real_component, color = 'b', name=signal_model.name)
        widget.plot_data(timevector, img_component, color = 'r', name=signal_model.name + " Imaginary",clear=False)

class FFTPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model):

        plot_item = widget.plot_widget.getPlotItem()
        plot_item.getViewBox().disableAutoRange(axis='x')

        widget.plot_widget.clear()

        num_samples = len(signal_model.data)

        yf = fft(signal_model.data, norm="ortho")
        xf = fftfreq(num_samples, 1 / signal_model.fs)[:num_samples // 2]

        widget.plot_widget.setLabel('bottom', 'Frequency ', units='Hz')
        widget.plot_widget.setLabel('left', 'Amplitude')

        widget.plot_widget.setTitle(f"Baseband FFT Spectrum")

        # find Sample where y is highest to plot that range on x Axis

        yf_idx_max = np.argmax(np.abs(yf))

        index_x = xf[yf_idx_max]

        x_range_idx_above = int(index_x + 250)
        x_range_idx_bottom = index_x - 250
        widget.plot_widget.setXRange(x_range_idx_bottom, x_range_idx_above)
        # widget.plot_widget.setYRange(0, 20, padding=0)

        widget.plot_data(xf,yf.real[:num_samples // 2], color = 'b', name=signal_model.name)

class PeriodogrammPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model):

        widget.plot_widget.clear()

        f, Pxx_den = signal.periodogram(signal_model.data, signal_model.fs, scaling='spectrum')

        widget.plot_widget.setLabel('bottom', 'Frequency ', units='Hz')
        widget.plot_widget.setLabel('left', 'Power/Frequency', units='V**2/Hz')

        widget.plot_widget.setTitle(f"Periodogram Spectrum")

        # find Sample where y is highest to plot that range on x Axis

        Pxx_den_idx_max = np.argmax(Pxx_den)

        index_x = f[Pxx_den_idx_max]

        x_window_size = 150
        widget.plot_widget.setXRange(index_x - x_window_size, index_x + x_window_size)

        y_max = np.max(Pxx_den) * 1.2
        widget.plot_widget.setYRange(0, y_max, padding=0)

        widget.plot_data(f,Pxx_den, color = 'b', name=signal_model.name)


class PlotManager:
    def __init__(self, widget: PlotWidget):
        self.widget = widget
        self.strategy = None

    def set_strategy(self, strategy: PlotStrategy):
        self.strategy = strategy

    def update_plot(self, signal_model):
        if self.strategy:
            self.strategy.plot(self.widget, signal_model)
