from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
# Use a relative import since base_plot is in the same folder
from .base_plot import SignalPlotCanvas


class SpectrumAnalyzerView(QWidget):

    def __init__(self, title_prefix="Spectrum", parent = None):

        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.plot_spectrogram = SignalPlotCanvas(title=f"{title_prefix}: Spectrogram")
        self.plot_fft = SignalPlotCanvas(title=f"{title_prefix}: FFT")

        self.tab_widget.addTab(self.plot_fft, "FFT")
        self.tab_widget.addTab(self.plot_spectrogram, "Spectrogram")

        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

class PulseDomainView(QWidget):

    def __init__(self, title_prefix="Pulse Signal", parent = None):

        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.plot_time = SignalPlotCanvas(title=f"{title_prefix}: Time Domain")
        self.plot_fft = SignalPlotCanvas(title=f"{title_prefix}: FFT")
        #self.plot_imp_response = PlotWidget(title=f"{title_prefix}: Impulse Response")

        self.tab_widget.addTab(self.plot_time, "Time Domain")
        self.tab_widget.addTab(self.plot_fft, "FFT")
        #self.tab_widget.addTab(self.plot_imp_response, "Impulse Response")

        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)