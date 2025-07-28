"""
Fast shutter using custom fastShutter.db support to use labjack and contorllable PS 
for actuation
    
"""

from ophyd import Component as Cpt
from ophyd import EpicsSignal, EpicsSignalRO
from apstools.devices.shutters import EpicsOnOffShutter

class fastShutter(EpicsOnOffShutter):
    """
    

    """
    signal = Cpt(EpicsSignal, "State", kind="config", string=True)
    readback = Cpt(EpicsSignalRO, "State_RBV", kind="config", string=True)

    @property
    def state(self) -> str:
        """is shutter "open", "close", or "unknown"?"""
        if self.readback.get() == self.open_value:
            result = self.valid_open_values[0]
        elif self.readback.get() == self.close_value:
            result = self.valid_close_values[0]
        else:
            result = self.unknown_state
        return result
