import os, sys
import msvcrt
import numpy as np
import yaml

from PyQt4.Qt import QApplication
from datetime import datetime

from Model._session import _session
from Model.camera import camera
from View.cameraMain import cameraMain
from Controller.devices.scmoscam import GEVSCMOS

if __name__ == '__main__':
    global session
    session = _session()
    base_dir = os.getcwd()
    session.base_dir = base_dir
    session.camera_config = os.path.join(base_dir,Config,'Trap_defaults_example.yml')

    with open(session.camera_config,'r') as f:
        data = yaml.load(f)

    if data['saving']['directory'] == '':
        savedir =os.path.joing(base_dir, str(datetime.now().date()))
    else:
        savedir = os.path.join(data['saving']['directory'],str(datetime.now().date()))

    if not os.path.exists(savedir):
        os.makedirs(savedir)
    session.saveDirectory = savedir
    session.filenameVideo = data['saving']['filenameVideo']
    session.filenamePhoto = data['saving']['filenameVideo']
    session.refreshTime = data['GUI']['refreshTime']
    session.lengthWaterfall = data['GUI']['lengthWaterfall']
    session.exposureTime = data['Camera']['exposureTime']
    PSL = GEVSCMOS(os.path.join(base_dir,'Controller','devices'), "SCMOS")
    cam = camera(PSL)
    cam.initializeCamera()
    session.camera['Model'] = 'PSI'
    app = QApplication(sys.argv)
    win = cameraMain(session,cam)
    win.show()
    sys.exit(app.exec_())
