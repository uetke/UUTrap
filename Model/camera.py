"""Classes and methods for working with cameras. It should provide an abstraction
layer for the most common uses of cameras.
"""
import h5py
import numpy as np
import yaml
from datetime import datetime

NUMPY_MODES = {"L":np.uint8, "I;16":np.uint16}
class camera():
    def __init__(self,camera):
        self.camera = camera
        self.running = False

    def initializeCamera(self):
        """Initializes the camera.
        """
        self.camera.Open()
        self.maxSize = self.camera.UpdateSizeMax()
        self.camera.SetClockSpeed('50MHz')
        self.camera.SetGainMode("gain1")
        self.camera.SetTrigger("FreeRunning")
        self.camera.EnableAutoLevel(0)
        self.camera.SetExposure(10,"Millisec")
        self.triggerCamera()

    def triggerCamera(self):
        """Triggers the camera.
        """
        self.camera.Snap()

    def setExposure(self,exposure):
        """Sets the exposure of the camera.
        """
        exposure = exposure*1000 # in order to always use microseconds
        while self.camera.GetStatus(): # Wait until exposure is finished.
            self.camera.SetExposure(np.int(exposure), 'Microsec')

    def readCamera(self):
        """Reads the camera
        """
        size,data = self.camera.GetImage()
        w,h = size
        mode = self.camera.GetMode()
        img = np.frombuffer(data,NUMPY_MODES[mode]).reshape((h,w))
        img = np.array(img)
        return np.transpose(img)

    def setROI(self,X,Y):
        """Sets up the ROI.
        """
        X -= 1
        Y -= 1
        # Left, top, right, bottom
        l = np.int(X[0])
        t = np.int(Y[0])
        r = np.int(X[1])
        b = np.int(Y[1])
        self.camera.SetSubArea(l,t,r,b)
        return self.camera.GetSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired.
        """
        return self.camera.GetSize()

    def setupCamera(self,params):
        """Setups the camera with the given parameters.
        -- params['exposureTime']
        -- params['binning']
        -- params['gain']
        -- params['frequency']
        -- params['ROI']
        """
        pass

    def getParameters(self):
        """Returns all the parameters passed to the camera, such as exposure time,
        ROI, etc. Not necessarily the parameters go to the hardware, it may be
        that some are just software related.
        Returns: dict = keyword => value.
        """
        pass

    def stopCamera(self):
        """Stops the acquisition
        """
        self.camera.AbortSnap()
        self.camera.Close()



def workerSaver(fileData,dic,q):
    """Function that can be run in a separate thread for continuously save data to disk.
    fileData -- STRING with the path to the file to use.
    dic -- A dictionary with metadata
    q -- Queue that will store all the images to be saved to disk.
    """
    f = h5py.File(fileData, "a") # This will append the file.
    now = str(datetime.now())
    g = f.create_group(now)
    allocate = 1000 # Number of frames to allocate along the z-axis.
    keep_saving = True # Flag that will stop the worker function if running in a separate thread.
    metaData = yaml.dump(dic)          # Has to be submitted via the queue a string 'exit'
    g.create_dataset('metadata',data=metaData)
    i=0
    while keep_saving:
        while not q.empty():
            img = q.get()
            if type(img)==type('exit'):
                keep_saving = False
            elif i == 0: # First time it runs, creates the dataset
                x = img.shape[0]
                y = img.shape[1]
                dset = g.create_dataset('timelapse', (x,y,allocate), maxshape=(x,y,None)) # The images are going to be stacked along the z-axis.
                dset[:,:,i] = img                                                                 # The shape along the z axis will be increased as the number of images increase.
                i+=1
            else:
                if i == dset.shape[2]:
                    dset.resize(i+allocate,axis=2)
                dset[:,:,i] = img
                i+=1
    f.flush()
    f.close()
