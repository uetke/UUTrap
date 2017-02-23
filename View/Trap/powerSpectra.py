'''
Created on 18 sep. 2015

@author: carattino
'''
import sys, os
import numpy as np
import pyqtgraph as pg
from datetime import datetime
from pyqtgraph.Qt import QtCore, QtGui
from Model.lib.xml2dict import variables
from matplotlib.backend_bases import CloseEvent

from Model.trap import Trap
from Model._session import _session

class powerSpectra(QtGui.QMainWindow):
    """ Main window for holding the Power Spectra widget.
    """
    def __init__(self,_session,parent=None):
        super(powerSpectra,self).__init__()

        # Layout
        self.setWindowTitle('Power Spectra')
        self.setGeometry(30,30,450,900)
        self.timetraces = PowerSpectraWidget()
        self.setCentralWidget(self.timetraces)

        self._session = _session

        # The class that controls the trap
        self.trap = Trap(_session)
        # Initialize the parameters
        self.time = _session.highSpeedTime # In seconds
        self.accuracy = _session.highSpeedAccuracy/1000 # In seconds

        num_points = int(self.time/self.accuracy)
        freqs = np.fft.rfftfreq(num_points, self.accuracy)
        initial_data = np.random.normal(size=(num_points))
        initial_ps = np.abs(np.fft.rfft(initial_data))**2

        self.freqs = freqs
        self.num_points = num_points

        self.curvex = self.timetraces.px.plot(freqs,initial_ps,pen='y')
        self.curvey = self.timetraces.py.plot(freqs,initial_ps,pen='y')
        self.curvez = self.timetraces.pz.plot(freqs,initial_ps,pen='y')

        self.connect(QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_S), self), QtCore.SIGNAL('activated()'), self.fileSave)

        self.workThread = workThread(self._session,self.trap)
        self.connect(self.workThread, QtCore.SIGNAL("QPD"), self.updateGUI )
        self.connect(self.workThread,  QtCore.SIGNAL('Stop_Tr'), self.stop_tr)
        self.setStatusTip('Running...')
        self.is_running = False # Status of the thread

        ##################
        # Build the menu #
        ##################
        exitAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/Signal-stop-icon.png'),'Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit the timetrace monitor in a safe way')
        exitAction.triggered.connect(self.exit_safe)

        saveAction = QtGui.QAction(QtGui.QIcon('GUI/Icons/floppy-icon.png'),'Save',self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Saves the currently displayed data to a file')
        saveAction.triggered.connect(self.fileSave)

        triggerTimetrace = QtGui.QAction('Start acquiring timetraces',self)
        triggerTimetrace.setShortcut('Ctrl+R')
        triggerTimetrace.setStatusTip('Click tu run the high priority ADwin process')
        triggerTimetrace.triggered.connect(self.update)

        stopTimetrace = QtGui.QAction('Stop timetrace',self)
        stopTimetrace.setStatusTip('Stops the acquisition after the current')
        stopTimetrace.triggered.connect(self.stop_acq)

        #self.statusBar()
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)
        powerMenu = menubar.addMenu('&Power Spectra')
        powerMenu.addAction(triggerTimetrace)
        powerMenu.addAction(stopTimetrace)

        self.statusbar = QtGui.QStatusBar()
        self.setStatusBar(self.statusbar)

    def stop_tr(self):
        """ Emmits a signal for stopping the timetraces.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))

    def stop_acq(self):
        """ Stops the continuous runs.
            Emmits a signal for continuing with the timetraces.
        """
        _session.runs = False
        self.emit(QtCore.SIGNAL('Start_Tr'))

    def update(self):
        """ Connects the signals of the working Thread with the appropriate
            functions in the main Class.
        """
        self.statusbar.showMessage('Running...')
        self.setStatusTip('Running...')
        if self.is_running == False:
            self.is_running = True
            self.workThread.start()
        else:
            print('Try to re-run')

    def updateGUI(self,frequencies,data,values):
        """Updates the curves in the screen and the mean values.
        """
        self.setStatusTip('Stopped...')
        self.is_running = False
        self.data = data
        self.freqs = frequencies
        self.curvex.setData(self.freqs[1:],values[1,1:])
        self.curvey.setData(self.freqs[1:],values[0,1:])
        self.curvez.setData(self.freqs[1:],values[2,1:])

        if self._session.runs: # If the continuous runs is activated, then refresh.
            self.update()


    def fileSave(self):
        """Saves the files to a specified folder.
        """
        name = 'PowerSpectra_Data'
        savedir = 'D:\\Data\\' + str(datetime.now().date()) + '\\'
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        i=1
        filename = name
        while os.path.exists(savedir+filename+".dat"):
            filename = '%s_%s' %(name,i)
            i += 1
        filename_params = filename +'_config.dat'
        filename = filename+".dat"
        np.savetxt("%s%s" %(savedir,filename), self.data,fmt='%s', delimiter=",")

        header = "Length, Integration Time"
        np.savetxt("%s%s"%(savedir,filename_params), [_session.time, _session.accuracy], header=header,fmt='%s',delimiter=',')

        # Saves the data to binary format. Sometimes (not sure why) the ascii data is not being save properly...
        # Only what would appear on the screen when printing self.data.
        try:
            np.save("%s%s" %(savedir,filename[:-4]), np.array(self.data))
        except:
            print('Error with Save')
            print(sys.exc_info()[0])
        print('Data saved in %s and configuration data in %s'%(savedir+filename,filename_params) )
        return

    def exit_safe(self):
        """ Exits the application stopping the working Thread.
        """
        if self._session.highSpeedTime>5:
            # To avoid impatience to force the shutdown.
            print('Waiting for the acquisition to finish.')
            print('It may take up to %s more seconds.'%_session.highSpeedTime)
        self.workThread.terminate()
        self.close()

    def closeEvent(self,evnt):
        """This function is called whenever the window is closed.
        """
        self.exit_safe()

class PowerSpectraWidget(QtGui.QWidget):
    """ Class for starting the needed windows and updating the screen.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('QPD Power Spectrum')

        self.layout = QtGui.QGridLayout(self)

        """ Power Spectrum """
        px = pg.PlotWidget()
        py = pg.PlotWidget()
        pz = pg.PlotWidget()


        self.layout.addWidget(px, 0, 0)
        self.layout.addWidget(py, 0, 1)
        self.layout.addWidget(pz, 1, 0)

        px.setLabel('left', "Power Spectrum X", units='U.A.')
        px.setLabel('bottom', "Frequency", units='Hz')
        px.setLogMode(x=True, y=True)

        py.setLabel('left', "Power Spectrum Y", units='U.A.')
        py.setLabel('bottom', "Frequency", units='Hz')
        py.setLogMode(x=True, y=True)

        pz.setLabel('left', "Power Spectrum Z", units='U.A.')
        pz.setLabel('bottom', "Frequency", units='Hz')
        pz.setLogMode(x=True, y=True)

        px.enableAutoRange('xy', True)
        py.enableAutoRange('xy', True)
        pz.enableAutoRange('xy', True)

        self.px = px
        self.py = py
        self.pz = pz

class workThread(QtCore.QThread):
    def __init__(self,_session,trap):
        QtCore.QThread.__init__(self)
        self._session = _session
        self.trap = trap
    def __del__(self):
        self.wait()

    def run(self):
        """ Triggers the ADwin to acquire a new set of data. It is a time consuming task.
        """
        num_points = int(self._session.highSpeedTime/self._session.highSpeedAccuracy*1000)
        freqs = np.fft.rfftfreq(num_points,self._session.highSpeedAccuracy/1000)

        """ Need to stop the monitor?
            If the monitor changes the position of the multiplexor, then it will
            alter the timing between the measurements.
        """
        self.emit(QtCore.SIGNAL('Stop_Tr'))

        """ Have to assume a particular order of the devices, i.e. QPDx->QPDy->QPDz"""
        dev = [self._session.devs['qpdx'],self._session.devs['qpdy'],self._session.devs['qpdz']]

        conditions = {}
        conditions['devs'] = dev
        conditions['time']  = self._session.highSpeedTime
        conditions['accuracy'] = self._session.highSpeedAccuracy
#        dev = _session.devices[0:4]
        fastData = self.trap.fastTimetrace(conditions)
        pwrx = np.abs(np.fft.rfft(fastData[0]))**2
        pwry = np.abs(np.fft.rfft(fastData[1]))**2
        pwrz = np.abs(np.fft.rfft(fastData[2]))**2

        values = np.zeros([4,len(pwrx)])
        data = np.zeros([3,len(fastData[0])])
        values[0,:] = pwrx
        values[1,:] = pwry
        values[2,:] = pwrz
        values[3,0] = np.mean(fastData[0])
        values[3,1] = np.mean(fastData[1])
        values[3,2] = np.mean(fastData[2])
        data[0,:] = fastData[0]
        data[1,:] = fastData[1]
        data[2,:] = fastData[2]

        self.emit( QtCore.SIGNAL('QPD'), freqs, fastData, values)
        return

if __name__ == '__main__':
    pass
