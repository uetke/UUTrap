""" Classes and routines useful for interacting with an optical trap.
"""
import yaml
import numpy as np

class Trap():
    def __init__(self,_session):
        """Class trap for condensing tasks that can be used for interacting with an optical trap.
        session -- class with important variables, including the adq card.
        """
        self._session = _session
        self.running = False
        stream = open(_session.task_conf,'r')
        self.tasks = yaml.load(stream)['task']
        self.monitorNum = []
        if self._session.adq['type'] == 'ni':
            self.adq = _session.adq['adq']
        else:
            raise Exception('Other types of cards not implemented for acquireAnalog')

    def triggerAnalog(self,conditions):
        """Triggers an analog measurement. It does not read the value.
        conditions -- a dictionary with the needed parameters for an analog acquisition.
        """
        if self._session.adq['type'] == 'ni':
            self.adq.analogSetup(conditions['channel'],conditions['points'],conditions['accuracy'],conditions['limits'])
            self.adq.analogTrigger() # Starts the measurement.
            self.running = True
        else:
            raise Exception('Other types of cards not implemented for acquireAnalog')

    def getAnalog(self,conditions):
        """Gets the analog values acquired with the triggerAnalog function.
        conditions -- dictionary with the number of points ot be read
        """
        if self._session.adq['type'] == 'ni':
            return self.adq.analogRead(conditions['points'])
        else:
            raise Exception('Other types of cards not implemented for getAnalog')

    def startMonitor(self,conditions):
        """Starts continuous acquisition of the specified channels with the specified timing interval.
        conditions['devs'] -- list of devices to monitor
        conditions['accuracy'] -- accuracy for the monitor. If not defined defaults to 0.1s
        """
        self.monitorTask = self.tasks['Monitor']
        channels = []
        if conditions['accuracy']>0:
            accuracy = conditions['accuracy']
        else:
            accuracy = 0.1 # 100 milliseconds
        if self._session.adq['type'] == 'ni':
            if type(conditions['devs']) == type(""):
                conditions['devs'] = [conditions['devs']]
            for dev in conditions['devs']:
                self.devsMonitor = len(conditions['devs'])
                if dev.properties['Type'] == 'Analog':
                    channels.append(dev.properties['Input']['Hardware']['PortID'])
                    limitmax = dev.properties['Input']['Limits']['Max']
                    limitmin = dev.properties['Input']['Limits']['Min']
                    # print('Channel: %s'%channels[-1])
                    # print('--- Limit Max: %s'%limitmax)
                    # print('--- Limit Min: %s'%limitmin)

            self.monitorNum = self.adq.analogSetup(self.monitorTask,channels,0,accuracy,(limitmin,limitmax))
            #for mon in self.monitorNum:
            self.adq.analogTrigger(self.monitorNum)

    def readMonitor(self):
        """Reads the monitor values of all the channels specified.
        """
        val,data = self.adq.analogRead(self.monitorNum,-1)
        return data[:val*self.devsMonitor]

    def stopMonitor(self):
        """Stops all the tasks related to the monitor.
        """
        if self._session.adq['type'] == 'ni':
            self.adq.clear(self.monitorNum)

    def fastTimetrace(self,conditions):
        """ Acquires a fast timetrace of the selected devices.
        conditions['devs'] -- list of devices to monitor
        conditions['accuracy'] -- accuracy in milliseconds.
        conditions['time'] -- total time of acquisition for each channel in seconds.
        """

        points = int(conditions['time']*1000/conditions['accuracy'])

        self.highSpeedTask = self.tasks['highSpeed']
        if self._session.adq['type'] == 'ni':
            if type(conditions['devs']) == type(""):
                conditions['devs'] = [conditions['dev']]
            data = []
            for dev in conditions['devs']:
                self.devsMonitor = len(conditions['devs'])
                if dev.properties['Type'] == 'Analog':
                    channel = dev.properties['Input']['Hardware']['PortID']
                    limitmax = dev.properties['Input']['Limits']['Max']
                    limitmin = dev.properties['Input']['Limits']['Min']
                    self.highSpeedNum = self.adq.analogSetup(self.highSpeedTask,channel,points,conditions['accuracy']/1000,(limitmin,limitmax))
                    self.adq.analogTrigger(self.highSpeedNum)
                    v,d = self.adq.analogRead(self.highSpeedNum,points,conditions['time'])
                    self.adq.clear(self.highSpeedNum)
                    data.append(np.array(d))
            return data
