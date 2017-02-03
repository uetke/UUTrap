"""
    ni6251.pi
    ---------
    Class for comunicating with the NI-6251 DAQ. It requires to have installed the DAQmx (provided by NI) and the pyDAQmx package (from pypy).
"""
from PyDAQmx import *
import numpy as np

class niDAQ():
    """Class for controlling a National Instruments NI-6251 DAQ.
    If using an expansin such as the SCC-68 it has to be properly configured throuh the NI-MAX software.
    """
    def __init__(self):
        self.read = int32()

    def acquire_analog(self,channel,points,accuracy,limits=(-10.0,10.0)):
        """Acquires an analog signal in the specified channel. The execution blocks the rest of the program.
        channel --  has to be defined as "Dev1/ai0", for example.
        points -- the total number of points to be acquired
        accuracy -- the time between acquisitions (in seconds)
        limits -- the limits of the expected values. A tuple of 2 values.
        Returns: numpy array of length points
        """
        self.task_Analog = TaskHandle()
        self.read = int32()
        points = int(points)
        data = np.zeros((points,), dtype=np.float64)
        channel = str.encode(channel)
        waiting_time = points*accuracy*1.05 # Adds a 5% waiting time in order to give enough time
        freq = 1/accuracy # Accuracy in seconds
        DAQmxCreateTask("",byref(self.task_Analog))
        DAQmxCreateAIVoltageChan(self.task_Analog,channel,"",DAQmx_Val_RSE,limits[0],limits[1],DAQmx_Val_Volts,None)
        DAQmxCfgSampClkTiming(self.task_Analog,"",freq,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,points)
        # DAQmx Start Code
        DAQmxStartTask(self.task_Analog)
        DAQmxReadAnalogF64(self.task_Analog,points,waiting_time,DAQmx_Val_GroupByChannel,data,points,byref(self.read),None)
        del self.task_Analog # releases the variable for use in other parts of the code
        return data

    def analogSetup(self,channel,points,accuracy,limits=(-10.0,10.0)):
        """Prepares the task for an analog measurement.
        channel --  has to be defined as "Dev1/ai0", for example.
        points -- the total number of points to be acquired
        accuracy -- the time between acquisitions (in seconds)
        limits -- the limits of the expected values. A tuple of 2 values.
        """
        self.task_Analog = TaskHandle()
        self.read = int32()
        points = int(points)
        data = np.zeros((points,), dtype=np.float64)
        channel = str.encode(channel)
        waiting_time = points*accuracy*1.05 # Adds a 5% waiting time in order to give enough time
        freq = 1/accuracy # Accuracy in seconds
        DAQmxCreateTask("",byref(self.task_Analog))
        DAQmxCreateAIVoltageChan(self.task_Analog,channel,"",DAQmx_Val_RSE,limits[0],limits[1],DAQmx_Val_Volts,None)
        DAQmxCfgSampClkTiming(self.task_Analog,"",freq,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,points)

    def analogTrigger(self):
        """Triggers the analog measurement.
        """
        if type(self.task_Analog) != type(TaskHandle()):
            raise Exception('Triggering an analog measurement before defining it')
        else:
            # DAQmx Start Code
            DAQmxStartTask(self.task_Analog)

    def analogRead(self,points):
        """Reads a number of points from the analog task.
        Returns a numpy array of length points.
        """
        if type(self.task_Analog) != type(TaskHandle()):
            raise Exception('Reading an analog measurement before defining it')
        else:
            self.read = int32()
            points = int(points)
            data = np.zeros((points,), dtype=np.float64)
            DAQmxReadAnalogF64(self.task_Analog,points,10,DAQmx_Val_GroupByChannel,data,points,byref(self.read),None)
            return data

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from time import time, sleep
    adq = niDAQ()
    points = 10000
    accuracy = 0.001
    adq.analogSetup('Dev1/ai7',points,accuracy)
    adq.analogTrigger()
    t0=time()
    while time()-t0<points*accuracy/5:
        print('Waiting...\n')
        sleep(1)
    data = adq.analogRead(points/10)
    x = np.linspace(0,points*accuracy,points/10)
    plt.plot(x,data,'o')
    plt.show()
