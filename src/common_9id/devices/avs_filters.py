"""
10-bank Filters from A-V-S

Device uses PyDevice for attenuation calculation and filter configuration
"""

#TODO how to adapt for new BITS format and devices.yml?

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import EpicsMotor

class AVSfilters(Device):

    
    
    
    
    atten_index = Component(EpicsSignal, "sortedIndex")
    atten_index_readback = Component(EpicsSignalRO, "sortedIndex_RBV")
    attenuation_set = Component(EpicsSignal, "attenuation")
    attenuation_readback = Component(EpicsSignalRO, "attenuation_actual")
    transmission_set = Component(EpicsSignal, "transmission")
    transmission_readback = Component(EpicsSignalRO, "transmission_RBV")
# TODO translation motor:   x_pos = Component(EpicsMotor, )
    
#filter_8ide = Filter2Device("8idPyFilter:FL2:", name="filter_8ide")
#filter_8idi = Filter2Device("8idPyFilter:FL3:", name="filter_8idi")
