from PySide6.QtWidgets import QWidget, QGridLayout

# Internal imports from your new plots package
from .base_plot import SignalPlotCanvas
from .containers import SpectrumAnalyzerView, PulseDomainView

class SignalMatrixView(QWidget):
    """
    The main plotting grid (Dashboard) of the application.
    Acts as a container for all signal analysis views.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main Grid Layout
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # 1. Pulse Domain Analysis (Top Left)
        self.plot_pulse = PulseDomainView(title_prefix="Pulse Shape")

        # 2. Constellation / Phase Space (Top Right)
        self.plot_const = SignalPlotCanvas(title="Constellation (I/Q)")
        self.plot_const.plot_widget.setAspectLocked(True)
        self.plot_const.plot_widget.showGrid(x=True, y=True)

        # 3. Baseband Analysis (Middle Row)
        self.plot_baseband = SignalPlotCanvas(title="Baseband (Time Domain)")
        self.bb_spectrum_container = SpectrumAnalyzerView(title_prefix="Baseband Spectrum")

        # 4. Bandpass Analysis (Bottom Row)
        self.plot_bandpass = SignalPlotCanvas(title="Bandpass (Time Domain)")
        self.bp_spectrum_container = SpectrumAnalyzerView(title_prefix="Bandpass Spectrum")

        # --- Grid Mapping ---
        # row, column
        layout.addWidget(self.plot_pulse, 0, 0)
        layout.addWidget(self.plot_const, 0, 1)

        layout.addWidget(self.plot_baseband, 1, 0)
        layout.addWidget(self.bb_spectrum_container, 1, 1)

        layout.addWidget(self.plot_bandpass, 2, 0)
        layout.addWidget(self.bp_spectrum_container, 2, 1)

    def clear_all_plots(self):
        """Helper method for the Mediator to reset the dashboard."""
        # This is a clean way for the Controller to reset the view layer
        self.plot_const.plot_widget.clear()
        # You can add more clear calls here for specific canvases