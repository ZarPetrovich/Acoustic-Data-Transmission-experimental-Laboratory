import pyqtgraph as pg
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget)
from adtx_lab.src.ui.style.color_pallete import LIGHT_THEME_RGB




class PlotWidget(QWidget):
    def __init__(self, title="Signal Plot", parent = None):

        super().__init__(parent)

        self.setObjectName("PlotContainer")

        self.layout = QVBoxLayout(self)
        #elf.layout.setContentsMargins(10, 10, 10, 10)

        self.plot_widget = pg.PlotWidget(title = title)
        #self.plot_widget.setBackground(LIGHT_THEME_RGB["bg-dark"])
        #self.plot_widget.showGrid(x = True, y = True)
        #elf.plot_widget.getPlotItem().setContentsMargins(10, 10, 30, 50)
        #elf.plot_widget_legend = pg.LegendItem(offset=(0, 0))
        #self.plot_widget_legend.setParentItem(self.plot_widget.getPlotItem())

        # Anchor legend to bottom center of the plot
        #self.plot_widget_legend.anchor((0.4,1.0), (1, 1.0))

        #self.plot_widget_legend.setOffset((40, -10))

        self.layout.addWidget(self.plot_widget)

        self.current_curve = None

    def plot_data(self, timevector, datavector, color='b', name="Signal", clear=True, stepMode=False):
        if clear:
            self.plot_widget.clear()
            # Remove all legend items when clearing
            #self.plot_widget_legend.clear()

        pen = pg.mkPen(color=color, width=2)
        self.current_curve = self.plot_widget.plot(timevector, datavector, pen=pen, name=name, stepMode = False)

        # Add the curve to the legend
        #elf.plot_widget_legend.addItem(self.current_curve, name)

        #self.plot_widget.enableAutoRange()
