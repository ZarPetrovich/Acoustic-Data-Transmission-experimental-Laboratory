import pyqtgraph as pg
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget)

class PlotWidget(QWidget):
    def __init__(self, title="Signal Plot", parent = None):

        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10,10,10,10)

        self.plot_widget = pg.PlotWidget(title = title)
        self.plot_widget.showGrid(x = True, y = True)
        self.layout.addWidget(self.plot_widget)


        self.current_curve = None

    def plot_data(self, timevector, datavector, color='b',name="Signal"):
        self.plot_widget.clear()
        self.plot_widget.addLegend()

        pen = pg.mkPen(color=color, width=2)
        self.current_curve = self.plot_widget.plot(timevector,datavector,pen=pen,name=name)

        self.plot_widget.enableAutoRange()
