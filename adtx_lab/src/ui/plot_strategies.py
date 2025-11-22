import numpy as np
from abc import ABC, abstractmethod
from adtx_lab.src.ui.plot_widgets import PlotWidget
from adtx_lab.src.dataclasses.signal_models import PulseSignal, BasebandSignal, BandpassSignal


class PlotStrategy(ABC):
    @abstractmethod
    def plot(self, widget:PlotWidget, signal_model):
        pass


class PulsePlotStrategy(PlotStrategy):

    def plot(self, widget: PlotWidget, signal_model: PulseSignal):

        num_samples = len(signal_model.data)
        timevector = np.arange(num_samples) / signal_model.fs

        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Pulse: {signal_model.name}")

        widget.plot_data(timevector, signal_model.data, color='b', name=signal_model.name)


class BasebandPlotStrategy(PlotStrategy):

    def plot(self, widget: PlotWidget, signal_model: BasebandSignal):

        num_samples = len(signal_model.data)
        timevector = np.arange(num_samples) / signal_model.fs

        widget.plot_widget.setLabel('bottom', 'Time', units='s')
        widget.plot_widget.setLabel('left', 'Amplitude', units='V')

        widget.plot_widget.setTitle(f"Baseband Signal: {signal_model.name}")

        widget.plot_data(timevector, signal_model.data, color = 'b', name=signal_model.name)


class PlotManager:
    def __init__(self, widget:PlotWidget):
        self.widget = widget
        self.strategy = None

    def set_strategy(self, strategy: PlotStrategy):
        self.strategy = strategy

    def update_plot(self, signal_model):
        if self.strategy:
            self.strategy.plot(self.widget, signal_model)
