import numpy as np
from abc import ABC, abstractmethod

from PySide6.QtCore import Qt # <<< ADDED
import pyqtgraph as pg # <<< ADDED


from adtx_lab.src.ui.plot_widgets import PlotWidget
from adtx_lab.src.dataclasses.signal_models import PulseSignal, BasebandSignal, BandpassSignal


class PlotStrategy(ABC):
    @abstractmethod
    def plot(self, widget:PlotWidget, signal_model):
        pass


class PulsePlotStrategy(PlotStrategy):

    def plot(self, widget: PlotWidget, signal_model: PulseSignal):

        num_samples = len(signal_model.data)

        symbol_period = float(1 / signal_model.fs)

        num_samples = len(signal_model.data)

        timevector = np.linspace(- (symbol_period * signal_model.span) / 2,
                (symbol_period * signal_model.span) / 2, num_samples, endpoint=True)

        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Pulse: {signal_model.name}")

        widget.plot_data(timevector, signal_model.data, color='b', name=signal_model.name)


class BasebandPlotStrategy(PlotStrategy):

    def plot(self, widget: PlotWidget, signal_model: BasebandSignal):

        num_samples = len(signal_model.data)
        timevector = np.arange(num_samples) / signal_model.fs

        real_component = np.real(signal_model.data)
        img_component = np.imag(signal_model.data)


        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Baseband Signal: {signal_model.name}")

        widget.plot_data(timevector, real_component, color = 'b', name=signal_model.name)
        widget.plot_data(timevector, img_component, color = 'r', name=signal_model.name + " Imaginary",clear=False)

class IterationPlotStrategy(PlotStrategy):

    def plot(self, widget: PlotWidget, signal_model: BasebandSignal):

        widget.plot_widget.clear()

        widget.plot_widget.setTitle(f"Iteration Buildup: {signal_model.pulse_name} on {signal_model.bit_seq_name}")
        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        # Calculate time vector for axis scaling
        num_samples = len(signal_model.data)
        timevector_full = np.arange(num_samples) / signal_model.fs
        max_time = timevector_full[-1]

        widget.plot_widget.setXRange(0, max_time, padding=0)

        # Use the full baseband signal to determine max amplitude for Y-range
        max_amp = np.max(np.abs(signal_model.data)) * 1.1
        widget.plot_widget.setYRange(-max_amp, max_amp, padding=0)

        # Add an item to display the iteration counter (using the internal pg.PlotWidget)
        self.text_item = pg.TextItem(
            text="Iteration: 0 / ?",
            anchor=(0, 0),
            color=(255, 255, 255)
        )
        widget.plot_widget.addItem(self.text_item)

        # Position the text item
        self.text_item.setPos(max_time * 0.9, max_amp * 0.9)



class PlotManager:
    def __init__(self, widget:PlotWidget):
        self.widget = widget
        self.strategy = None

    def set_strategy(self, strategy: PlotStrategy):
        self.strategy = strategy

    def update_plot(self, signal_model):
        if self.strategy:
            self.strategy.plot(self.widget, signal_model)
