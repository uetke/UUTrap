'''
Created on 18 sep. 2015

@author: aj carattino

Widget for displaying the values of the signals acquired with the program.

'''


import sys
from pyqtgraph.Qt import QtGui


class valueMonitor(QtGui.QWidget):
    """ Widget for displaying as LCD numbers the values of different channels.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle('Values Monitor')
        self.setGeometry(30,30,400,400)
        self.layout = QtGui.QGridLayout(self)

        newfont = QtGui.QFont("Times", 40, QtGui.QFont.Bold)

        self.qpdx_label = QtGui.QLabel(self)
        self.qpdx_label.setText('QPDx: ')
        self.qpdx_label.setFont(newfont)
        self.qpdx = QtGui.QLCDNumber()
        self.qpdx.setDigitCount(5)
        self.qpdx.display(1)

        self.qpdy_label = QtGui.QLabel(self)
        self.qpdy_label.setText('QPDy: ')
        self.qpdy_label.setFont(newfont)
        self.qpdy = QtGui.QLCDNumber()
        self.qpdy.setDigitCount(5)
        self.qpdy.display(2)

        self.qpdz_label = QtGui.QLabel(self)
        self.qpdz_label.setText('QPDz: ')
        self.qpdz_label.setFont(newfont)
        self.qpdz = QtGui.QLCDNumber()
        self.qpdz.setDigitCount(5)
        self.qpdz.display(3)

        self.layout.addWidget(self.qpdx_label,0,0)
        self.layout.addWidget(self.qpdx,0,1)
        self.layout.addWidget(self.qpdy_label,1,0)
        self.layout.addWidget(self.qpdy,1,1)
        self.layout.addWidget(self.qpdz_label,2,0)
        self.layout.addWidget(self.qpdz,2,1)

    def UpdateValues(self,data):
        ''' Updates the values displayed. Asumes a particular order of the data being passed
        '''
        self.qpdx.display(data[0])
        self.qpdy.display(data[1])
        self.qpdz.display(data[2])


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    test = ValueMonitor()
    test.show()
    app.exec_()
