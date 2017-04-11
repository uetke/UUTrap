"""Run this program to start the GUI for controlling the optical tweezer
"""
import os
import sys
from Controller.devices.ni6251 import niDAQ
from Model._session import _session
from Model.trap import Trap
from View.Trap.mainWindow import mainWindow
from Model.lib.xml2dict import device

from PyQt4.Qt import QApplication

_session = _session()

base_dir = os.path.abspath(os.path.dirname(__file__))
_session.dev_conf = os.path.join(base_dir,'config','config_devices.xml')
_session.task_conf = os.path.join(base_dir,'config','config_tasks.yml')
_session.adq['dev'] = device(type='',name='NI',filename=_session.dev_conf)
_session.adq['adq'] = niDAQ(device_number=_session.adq['dev'].properties['device_number'])
_session.adq['type'] = 'ni'

_session.saveDirectory = 'G:\\Data\\'

qpdx = device('qpdx')
qpdy = device('qpdy')
qpdz = device('qpdz')
_session.monDevs = {'qpdx':qpdx,'qpdy':qpdy,'qpdz':qpdz}
_session.devs = {'qpdx':qpdx,'qpdy':qpdy,'qpdz':qpdz}

trap = Trap(_session)

app = QApplication(sys.argv)
mon = mainWindow(_session)
mon.show()
sys.exit(app.exec_())
