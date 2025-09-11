"""
Aerotech Hexapod

Device uses PyDevice for focal size calculation and lens configuration control

    Parameters
    ==========
    prefix:
      EPICS prefix required to communicate with hexapod IOC, ex: "9idAerotech:"
    x:
      The motor record PV controlling the virtual axis x "m7"
    y:
      The motor record PV controlling the virtual axis y "m8"
    z:
      The motor record PV controlling the virtual axis z "m9"
    ax:
      The motor record PV controlling the virtual axis ax "m10"
    ay:
      The motor record PV controlling the virtual axis ay "m11"
    az:
      The motor record PV controlling the virtual axis az "m12"

"""

import logging
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import EpicsMotor
from ophyd import PVPositioner

logger = logging.getLogger(__name__)
logger.info(__file__)
    
class aerotechHexapod(Device):
    '''
    Handles single transfocator system
    
    '''
    def __init__(
        self,
        prefix: str,
        x: str,
        y: str,
        z: str,
        ax: str,
        ay: str,
        az: str,
        *args,
        **kwargs,
    ):
        self._prefix = prefix
        self._x_motor = prefix+x
        self._y_motor = prefix+y
        self._z_motor = prefix+z
        self._ax_motor = prefix+ax
        self._ay_motor = prefix+ay
        self._az_motor = prefix+az
        super().__init__(prefix, *args, **kwargs)

    x = FCpt(EpicsMotor,"{_x_motor}" , kind="hinted", labels={"motors"})
    y = FCpt(EpicsMotor,"{_y_motor}" , kind="hinted", labels={"motors"})
    z = FCpt(EpicsMotor,"{_z_motor}" , kind="hinted", labels={"motors"})
    ax = FCpt(EpicsMotor,"{_ax_motor}" , kind="hinted", labels={"motors"})
    ay = FCpt(EpicsMotor,"{_ay_motor}" , kind="hinted", labels={"motors"})
    az = FCpt(EpicsMotor,"{_az_motor}" , kind="hinted", labels={"motors"})

    strut1 = Cpt(EpicsSignalRO, "strut1" , kind="hinted", labels={"motors"})
    strut2 = Cpt(EpicsSignalRO, "strut2" , kind="hinted", labels={"motors"})
    strut3 = Cpt(EpicsSignalRO, "strut3" , kind="hinted", labels={"motors"})
    strut4 = Cpt(EpicsSignalRO, "strut4" , kind="hinted", labels={"motors"})
    strut5 = Cpt(EpicsSignalRO, "strut5" , kind="hinted", labels={"motors"})
    strut6 = Cpt(EpicsSignalRO, "strut6" , kind="hinted", labels={"motors"})
    
