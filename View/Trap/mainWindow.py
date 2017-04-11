'''
@author: aj carattino
'''
import numpy as np
import sys
import os
import copy

from pyqtgraph.Qt import QtGui, QtCore
from PyQt4.Qt import QApplication
from datetime import datetime

from Model.trap import Trap
from View.Trap.Monitor import monitorWidget
from View.Trap.powerSpectra import powerSpectra
from View.Trap.configWindow import configWindow
from View.Trap.valueMonitor import valueMonitor

class mainWindow(QtGui.QMainWindow):
    """ Monitor of the relevant signals.
    """
    def __init__(self,_session,parent=None):
        super(mainWindow,self).__init__()
        self.setWindowTitle('Signal Monitor')
        self.setGeometry(30,30,1200,900)

        # The class that controls the trap
        self.trap = Trap(_session)

        # The windows that are available
        self.timetraces = monitorWidget()
        self.powerSpectra = powerSpectra(_session)
        self.configWindow = configWindow(_session)
        self.valueMonitor = valueMonitor()
        self.setCentralWidget(self.timetraces)

        # The devices to analize
        self.devices = []
        self.devices.append(_session.devs['qpdx'])
        self.devices.append(_session.devs['qpdy'])
        self.devices.append(_session.devs['qpdz'])

        self._session = _session
        # Initial timetrace data
        self.clearMonitor()


        self.qpdx = self.timetraces.qpdx.plot(self.t[0],self.data[0],pen='y')
        self.qpdy = self.timetraces.qpdy.plot(self.t[1],self.data[1],pen='y')
        self.qpdz = self.timetraces.qpdz.plot(self.t[2],self.data[1],pen='y')

        self.varx = self.timetraces.varx.plot(self.t[0],self.data[0],pen='y')
        self.vary = self.timetraces.vary.plot(self.t[1],self.data[1],pen='y')
        self.varz = self.timetraces.varz.plot(self.t[2],self.data[1],pen='y')

        self.ctimer = QtCore.QTimer()
        self.running = False

        QtCore.QObject.connect(self.ctimer,QtCore.SIGNAL("timeout()"),self.updateMon)
        QtCore.QObject.connect(self,QtCore.SIGNAL("TimeTraces"),self.updateTimes)
        QtCore.QObject.connect(self,QtCore.SIGNAL("varData"),self.updateVariances)
        QtCore.QObject.connect(self.powerSpectra, QtCore.SIGNAL('Stop_Tr'),self.stop_timer)
        QtCore.QObject.connect(self,QtCore.SIGNAL('MeanData'),self.valueMonitor.UpdateValues)
        QtCore.QObject.connect(self.configWindow,QtCore.SIGNAL('Times'),self.updateParameters)
        QtCore.QObject.connect(self.configWindow, QtCore.SIGNAL('clearMonitor'), self.clearMonitor)

        ###################
        # Define the menu #
        ###################

        saveAction = QtGui.QAction(QtGui.QIcon('View/Icons/floppy-icon.png'),'Save',self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save the displayed data')
        saveAction.triggered.connect(self.fileSave)

        exitAction = QtGui.QAction(QtGui.QIcon('View/Icons/Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the program in a safe way')
        exitAction.triggered.connect(self.exit_safe)

        configureTimes = QtGui.QAction(QtGui.QIcon('View/Icons/pinion-icon.png'),'Configure',self)
        configureTimes.setShortcut('Ctrl+T')
        configureTimes.setStatusTip('Configure the acquisition times')
        configureTimes.triggered.connect(self.configWindow.show)

        runMonitor = QtGui.QAction('Run Monitor',self)
        runMonitor.setShortcut('Ctrl+R')
        runMonitor.setStatusTip('Starts running the monitor of signals')
        runMonitor.triggered.connect(self.start_timer)

        stopMonitor = QtGui.QAction('Stop Monitor',self)
        stopMonitor.setStatusTip('Stops running the monitor of signals')
        stopMonitor.triggered.connect(self.stop_timer)

        showvalueMonitor = QtGui.QAction('Value Monitor',self)
        showvalueMonitor.setShortcut('Ctrl+V')
        showvalueMonitor.setStatusTip('Shows the Value Monitor')
        showvalueMonitor.triggered.connect(self.valueMonitor.show)

        acquireTimetrace = QtGui.QAction('Power Spectra',self)
        acquireTimetrace.setStatusTip('Show the Power Spectra window')
        acquireTimetrace.triggered.connect(self.powerSpectra.show)

        triggerTimetrace = QtGui.QAction('Start acquiring timetraces',self)
        triggerTimetrace.setStatusTip('Click tu run the high priority ADwin process')
        triggerTimetrace.triggered.connect(self.powerSpectra.update)

        stopTimetrace = QtGui.QAction('Stop timetrace',self)
        stopTimetrace.setStatusTip('Stops the acquisition after the current')
        stopTimetrace.triggered.connect(self.powerSpectra.stop_acq)

        self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        confgMenu = menubar.addMenu('&Configure')
        confgMenu.addAction(configureTimes)

        monitorMenu = menubar.addMenu('&Monitor')
        monitorMenu.addAction(runMonitor)
        monitorMenu.addAction(stopMonitor)
        monitorMenu.addAction(showvalueMonitor)

        traceMenu = menubar.addMenu('&Timetraces')
        traceMenu.addAction(acquireTimetrace)
        traceMenu.addAction(triggerTimetrace)
        traceMenu.addAction(stopTimetrace)

    def clearMonitor(self):
        """Clears the variables associated with the monitor and starts again. """
        self.t =[]
        self.data = []
        self.varData = []
        self.varT = []
        self.firstMon = []
        self.firstVar = []
        for i in range(len(self.devices)):
            self.t.append(np.zeros([1,]))
            self.data.append(np.zeros([1,]))
            self.varData.append(np.zeros([1,]))
            self.varT.append(np.zeros([1,]))
            self.firstMon.append(True)
            self.firstVar.append(True)

    def updateMon(self):
        """Function that gets the data from the ADQ and prepares it for updating the GUI.
        """

        final_data = self.trap.readMonitor() # Have to be sure it is an ND array
        final_data = np.reshape(final_data, (self.trap.devsMonitor, int(len(final_data)/self.trap.devsMonitor)))
        mean_data = np.mean(final_data,1)
        varData = np.var(final_data, 1)
        self.emit(QtCore.SIGNAL('TimeTraces'), final_data)
        self.emit(QtCore.SIGNAL('varData'), varData)
        self.emit(QtCore.SIGNAL('MeanData'), mean_data)  # For updating values in an external dialog

    def updateTimes(self,data):
        """Updates the plots of the timetraces.
        """
        #Check the sizes of the variances
        var = copy.copy(data)
        for i in range(len(var)):
            xdata = np.arange(len(var[i]))*self._session.monitorTimeresol/1000
            old_data = self.data[i]
            old_t = self.t[i]
            self.t[i] = np.append(self.t[i], xdata+max(self.t[i]) + self._session.monitorTimeresol/1000)
            self.data[i] = np.append(self.data[i],var[i])
            limit = int(self._session.monitorTime/self._session.monitorTimeresol*1000)
            if self.firstMon[i]:
                limit = len(self.t[i])-1
                self.firstMon[i] = False
            self.t[i] = self.t[i][-limit:]
            self.data[i] = self.data[i][-limit:]

        self.qpdx.setData(self.t[0],self.data[0])
        self.qpdy.setData(self.t[1],self.data[1])
        self.qpdz.setData(self.t[2],self.data[2])

    def updateVariances(self, data):
        var = copy.copy(data)
        for i in range(len(var)):
            xdata = self._session.monitorRefresh/1000
            self.varT[i] = np.append(self.varT[i], xdata + max(self.varT[i]) + self._session.monitorRefresh/1000)
            self.varData[i] = np.append(self.varData[i], var[i])
            limit = int(self._session.monitorTime/self._session.monitorRefresh*1000)
            if self.firstVar[i]:
                limit = len(self.varT[i])-1
                self.firstVar[i] = False
            self.varT[i] = self.varT[i][-limit:]
            self.varData[i] = self.varData[i][-limit:]

        self.varx.setData(self.varT[0], self.varData[0])
        self.vary.setData(self.varT[1], self.varData[1])
        self.varz.setData(self.varT[2], self.varData[2])

    def start_timer(self):
        """Starts the timer with a predefined update interval.
        It also starts the monitor routine.
        """
        if not self.running:
            if self.powerSpectra.is_running:
                print('Cant update while power spectra is running.')
            else:
                conditions = {}
                # Starts the timer for updating the GUI
                conditions['devs'] = self.devices
                conditions['accuracy'] = self._session.monitorTimeresol/1000 # In seconds
                self.trap.startMonitor(conditions)
                self.ctimer.start(self._session.monitorRefresh)

                self.running = True
        else:
            self.stop_timer()

    def stop_timer(self):
        """Stops refreshing and the monitor.
        """
        self.ctimer.stop()
        if self.running:
            self.trap.stopMonitor()
        self.running = False

    def fileSave(self):
        """Saves the files to a specified folder.
        """
        name = 'Timetrace_Data'
        savedir = os.path.join(self._session.saveDirectory, str(datetime.now().date()))
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        i=1
        filename = name
        while os.path.exists(savedir+filename+".dat"):
            filename = '%s_%s' %(name,i)
            i += 1

        filename = filename+".dat"
        np.savetxt("%s%s" %(savedir, filename), [self.t, self.data], fmt='%s', delimiter=",")

        # Saves the data to binary format. Sometimes (not sure why) the ascii data is not being save properly...
        # Only what would appear on the screen when printing self.data.
        try:
            np.save("%s%s" %(savedir,filename[:-4]), np.array(self.data))
        except:
            print('Error with Save')
            print(sys.exc_info()[0])

        print('Data saved in %s'%(savedir+filename) )
        return

    def updateParameters(self,_session):
        """Updates the relevant parameters for the monitor timetrace.
        """
        self._session = _session
        self.powerSpectra._session = _session
        self.configWindow._session = _session
        self.stop_timer()
        self.start_timer()

    def closeEvent(self,evnt):
        """Triggered at closing.
        """
        self.exit_safe()

    def exit_safe(self):
        """ Exits the application.
        """
        self.powerSpectra.exit_safe()
        self.configWindow.close()
        self.stop_timer()
        self.trap.stopMonitor()
        self.close()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mon = Monitor()
    mon.show()
    sys.exit(app.exec_())
