import pyqtgraph as pg
from pyqtgraph.Qt import QtGui


class monitorWidget(QtGui.QWidget):
    """ Widget for displaying the Timetraces.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        # Timetraces
        qpdx = pg.PlotWidget()
        qpdy = pg.PlotWidget()
        qpdz = pg.PlotWidget()
        varx = pg.PlotWidget()
        vary = pg.PlotWidget()
        varz = pg.PlotWidget()

        qpdx.setLabel('left', "QPD X", units='V')
        qpdx.setLabel('bottom', "Time", units='s')
        qpdy.setLabel('left', "QPD Y", units='V')
        qpdy.setLabel('bottom', "Time", units='s')
        qpdz.setLabel('left', "QPD Z", units='V')
        qpdz.setLabel('bottom', "Time", units='s')

        varx.setLabel('left', "QPD X", units='V')
        varx.setLabel('bottom', "Time", units='s')
        vary.setLabel('left', "QPD Y", units='V')
        vary.setLabel('bottom', "Time", units='s')
        varz.setLabel('left', "QPD Z", units='V')
        varz.setLabel('bottom', "Time", units='s')

        self.qpdx = qpdx
        self.qpdy = qpdy
        self.qpdz = qpdz
        self.varx = varx
        self.vary = vary
        self.varz = varz

        # Layout
        self.layout = QtGui.QGridLayout(self)
        self.layout.addWidget(self.qpdx, 0, 0)
        self.layout.addWidget(self.qpdy, 1, 0)
        self.layout.addWidget(self.qpdz, 2, 0)

        self.layout.addWidget(self.varx, 0, 1)
        self.layout.addWidget(self.vary, 1, 1)
        self.layout.addWidget(self.varz, 2, 1)
