from pyqtgraph.Qt import QtCore, QtGui
from Model._session import _session

class configWindow(QtGui.QWidget):
    """ Simple class to change the values for the acquisition times.
    """
    def __init__(self,_session,parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._session = _session
        self.setWindowTitle('Configure the times')
        self.setGeometry(30,30,100,100)
        self.layout = QtGui.QGridLayout(self)

        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFont.setPointSize(15)
        '''=================TIMETRACES======================================='''
        self.timetraces_title = QtGui.QLabel(self)
        self.timetraces_title.setText('Timetraces')
        self.timetraces_title.setAlignment(QtCore.Qt.AlignHCenter)
        self.timetraces_title.setFont(titleFont)

        self.highSpeedTime_label = QtGui.QLabel(self)
        self.highSpeedTime_label.setText('Time (s): ')
        self.highSpeedTime_label.setAlignment(QtCore.Qt.AlignRight)
        self.highSpeedTime = QtGui.QLineEdit(self)
        self.highSpeedTime.setText(str(_session.highSpeedTime))
        self.highSpeedAccuracy_label = QtGui.QLabel(self)
        self.highSpeedAccuracy_label.setText('Accuracy (ms): ')
        self.highSpeedAccuracy_label.setAlignment(QtCore.Qt.AlignRight)
        self.highSpeedAccuracy = QtGui.QLineEdit(self)
        self.highSpeedAccuracy.setText(str(_session.highSpeedAccuracy))
        '''==================MONITOR========================================='''
        self.monitor_title = QtGui.QLabel(self)
        self.monitor_title.setText('Monitor')
        self.monitor_title.setFont(titleFont)
        self.monitor_title.setAlignment(QtCore.Qt.AlignHCenter)

        self.monitorTime_label = QtGui.QLabel(self)
        self.monitorTime_label.setText('Monitor timetrace (s)')
        self.monitorTime_label.setAlignment(QtCore.Qt.AlignRight)
        self.monitorTime = QtGui.QLineEdit(self)
        self.monitorTime.setText(str(_session.monitorTime))
        self.monitorTimeresol_label = QtGui.QLabel(self)
        self.monitorTimeresol_label.setText('Monitor resolution (ms)')
        self.monitorTimeresol_label.setAlignment(QtCore.Qt.AlignRight)
        self.monitorTimeresol = QtGui.QLineEdit(self)
        self.monitorTimeresol.setText(str(_session.monitorTimeresol))
        self.monitorRefresh_label = QtGui.QLabel(self)
        self.monitorRefresh_label.setText('Monitor refresh (ms):')
        self.monitorRefresh_label.setAlignment(QtCore.Qt.AlignRight)
        self.monitorRefresh = QtGui.QLineEdit(self)
        self.monitorRefresh.setText(str(_session.monitorRefresh))
        '''================================================================='''

        self.contin_runs = QtGui.QCheckBox('Continuous runs', self)
        self.contin_runs.setChecked(_session.runs)

        self.applyButton = QtGui.QPushButton('Apply', self)
        self.applyButton.clicked[bool].connect(self.setTimes)

        self.clearMonitor = QtGui.QPushButton('Clear monitor', self)
        self.clearMonitor.clicked[bool].connect(self.clearMonitor)

        self.layout.addWidget(self.timetraces_title,0,0,1,0)
        self.layout.addWidget(self.highSpeedTime_label,1,0)
        self.layout.addWidget(self.highSpeedTime,1,1)
        self.layout.addWidget(self.highSpeedAccuracy_label,2,0)
        self.layout.addWidget(self.highSpeedAccuracy,2,1)
        self.layout.addWidget(self.monitor_title,3,0,1,0)
        self.layout.addWidget(self.monitorTime_label,4,0)
        self.layout.addWidget(self.monitorTime,4,1)
        self.layout.addWidget(self.monitorTimeresol_label,5,0)
        self.layout.addWidget(self.monitorTimeresol,5,1)
        self.layout.addWidget(self.monitorRefresh_label,6,0)
        self.layout.addWidget(self.monitorRefresh,6,1)

        self.layout.addWidget(self.contin_runs,7,0)

        self.layout.addWidget(self.applyButton,8,0,1,2)
        self.layout.addWidget(self.clearMonitor,9,0,1,2)

    def setTimes(self):
        highSpeedTime = float(self.highSpeedTime.text())
        highSpeedAccuracy = float(self.highSpeedAccuracy.text())/1000

        monitorTime = float(self.monitorTime.text())
        monitorTimeresol = float(self.monitorTimeresol.text())
        monitorRefresh = float(self.monitorRefresh.text())

        self._session.highSpeedTime = highSpeedTime
        self._session.highSpeedAccuracy = highSpeedAccuracy
        self._session.runs = self.contin_runs.isChecked()
        self._session.monitorTime = monitorTime
        self._session.monitorTimeresol = monitorTimeresol
        self._session.monitorRefresh = monitorRefresh

        self.emit( QtCore.SIGNAL('Times'), self._session)

    def clearMonitor(self):
        self.emit(QtCore.SIGNAL('clearMonitor'))
