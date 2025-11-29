import numpy as np
from abc import ABC, abstractmethod
import pyqtgraph as pg

from adtx_lab.src.ui.plot_widgets import PlotWidget
from adtx_lab.src.dataclasses.signal_models import PulseSignal, ConstellationSignal
from adtx_lab.src.constants import PulseShape

class PlotStrategy(ABC):
    @abstractmethod
    def plot(self, widget: PlotWidget, signal_model):
        pass

class PulsePlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model: PulseSignal):
        widget.plot_widget.clear()

        # Time Vector Calculation
        symbol_period = 1 / signal_model.sym_rate
        # For Rectangle/Cosine, length is determined by span * samples_per_symbol
        # We can infer time from fs and data length
        t_duration = len(signal_model.data) / signal_model.fs

        # Center the pulse around 0
        timevector = np.linspace(-t_duration/2, t_duration/2, len(signal_model.data))

        widget.plot_widget.setTitle(f"Pulse: {signal_model.name}")
        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_data(timevector, signal_model.data, color='cyan', name=signal_model.name)

class ConstellationPlotStrategy(PlotStrategy):
    def plot(self, widget: PlotWidget, signal_model: ConstellationSignal):
        widget.plot_widget.clear()
        widget.plot_widget.setTitle(f"Constellation: {signal_model.name}")
        widget.plot_widget.setLabel('bottom', 'In-Phase (I)')
        widget.plot_widget.setLabel('left', 'Quadrature (Q)')

        # Force square aspect ratio
        widget.plot_widget.setAspectLocked(True)

        i_data = np.real(signal_model.data)
        q_data = np.imag(signal_model.data)

        # Create Scatter Plot
        scatter = pg.ScatterPlotItem(
            size=15,
            pen=pg.mkPen('w', width=1),
            brush=pg.mkBrush(100, 100, 255, 200),
            hoverable=True
        )
        scatter.addPoints(i_data, q_data)

        widget.plot_widget.addItem(scatter)

        # Add Crosshairs
        widget.plot_widget.addLine(x=0, pen=pg.mkPen('w', style=pg.QtCore.Qt.DashLine))
        widget.plot_widget.addLine(y=0, pen=pg.mkPen('w', style=pg.QtCore.Qt.DashLine))

class PlotManager:
    def __init__(self, widget: PlotWidget):
        self.widget = widget
        self.strategy = None

    def set_strategy(self, strategy: PlotStrategy):
        self.strategy = strategy

    def update_plot(self, signal_model):
        if self.strategy:
            self.strategy.plot(self.widget, signal_model)