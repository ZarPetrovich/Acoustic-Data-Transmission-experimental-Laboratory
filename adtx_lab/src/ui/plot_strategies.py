import numpy as np
from abc import ABC, abstractmethod
import pyqtgraph as pg

from adtx_lab.src.ui.plot_widgets import PlotWidget
from adtx_lab.src.dataclasses.signal_models import PulseSignal, ConstellationSignal, BasebandSignal
from adtx_lab.src.constants import PulseShape




class PlotStrategy(ABC):
    @abstractmethod
    def plot(self, widget: PlotWidget, signal_model):
        pass


class PulsePlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model: PulseSignal):
        widget.plot_widget.clear()

        # Time Vector Calculation
        t_duration = len(signal_model.data) / signal_model.fs

        # Center the pulse around 0
        timevector = np.linspace(-t_duration/2, t_duration/2, len(signal_model.data))

        widget.plot_widget.setTitle(f"Pulse: {signal_model.name}")
        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_data(timevector, signal_model.data, color='cyan', name=signal_model.name)


class ConstellationPlotStrategy(PlotStrategy):
    """
    Plots the constellation diagram, including bit labels next to each symbol point.
    """
    def plot(self, widget: PlotWidget, signal_model: ConstellationSignal):
        widget.plot_widget.clear()
        widget.plot_widget.setTitle(f"Constellation: {signal_model.name}")
        widget.plot_widget.setLabel('bottom', 'In-Phase (I / Real)')
        widget.plot_widget.setLabel('left', 'Quadrature (Q / Imaginary)')

        widget.plot_widget.setAspectLocked(True)

        dict_look_up_table = signal_model.look_up_table

        # --- 1. Plot the Symbols ---

        # Prepare data for plotting
        complex_symbols = np.array(list(dict_look_up_table.values()))
        i_data = complex_symbols.real
        q_data = complex_symbols.imag

        # Create Scatter Plot Item (Dots)
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


        # --- 3. Add Crosshairs and Tidy Up ---

        # Add Crosshairs (Axes)
        widget.plot_widget.addLine(x=0, pen=pg.mkPen('w', style=pg.Qt.DashLine))
        widget.plot_widget.addLine(y=0, pen=pg.mkPen('w', style=pg.Qt.DashLine))

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


class PlotManager:
    def __init__(self, widget: PlotWidget):
        self.widget = widget
        self.strategy = None

    def set_strategy(self, strategy: PlotStrategy):
        self.strategy = strategy

    def update_plot(self, signal_model):
        if self.strategy:
            self.strategy.plot(self.widget, signal_model)
