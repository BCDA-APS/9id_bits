"""
JJ-Xray Transfocators

Device uses PyDevice for focal size calculation and lens configuration control
"""

#TODO how to adapt for new BITS format and devices.yml?

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO


#TODO PVs to add:
# RB: q, dq, z-offsets
# RB: binary control, ind. control, rbv  (both CRL for 2x)
# Control: beamMode (+ RBV), energySelect
# Busy, crl

# Break into 1x and 2x and common

class JJtransfocator(Device):

    fpower_index = Component(EpicsSignal, "1:sortedIndex", kind="hinted")
    fpower_index_readback = Component(EpicsSignalRO, "1:sortedIndex_RBV", kind="hinted")
    fsize_set = Component(EpicsSignal, "focalSize", kind="hinted")
    fsize_readback = Component(EpicsSignalRO, "focalSize_actual", kind="hinted")
    q = Component(EpicsSignalRO, "q", kind="hinted")
    dq = Component(EpicsSignalRO, "dq", kind="hinted")
    sam_position_readback = Component(EpicsSignalRO, "samplePosition_RBV", kind="hinted")
    sam_position_offset_readback = Component(EpicsSignalRO, "samplePositionOffset_RBV", kind="hinted")

    energy_keV_local = Component(EpicsSignal, "EnergyLocal", kind="config")
    energy_keV_mono = Component(EpicsSignalRO, "EnergyBeamline", kind="config")
    energy_keV_lookup = Component(EpicsSignalRO, "energy_rbv", kind="hinted")
    
    beamMode = Component(EpicsSignal, "beamMode", string=True, kind="config")
    energyMode = Component(EpicsSignal, "energySelect", string=True, kind="config")

    
class JJtransfocator1x(JJtransfocator):
    '''
    Handles single transfocator system
    
    '''
    binary_crl1_config = Component(EpicsSignalRO, "1:lenses", kind="hinted")
    bw_crl1_config = Component(EpicsSignalRO, "1:lensConfig_BW")
    rbv_crl1_config = Component(EpicsSignalRO, "1:lensConfig_RBV", kind="hinted")

    crl1_z_pos = Component(EpicsSignalRO, "1:oePositionOffset_RBV")

    interLensDelay1 = Component(EpicsSignal, "1:interLensDelay", kind="config")
    
    #TODO gross motors
    
class JJtransfocator2x(JJtransfocator1x):
    
    '''
    Adds a second transfocator to beamline
    
    '''
    binary_crl2_config = Component(EpicsSignalRO, "2:lenses", kind="hinted")
    bw_crl2_config = Component(EpicsSignalRO, "2:lensConfig_BW")
    rbv_crl2_config = Component(EpicsSignalRO, "2:lensConfig_RBV", kind="hinted")

    crl2_z_pos = Component(EpicsSignalRO, "2:oePositionOffset_RBV")

    interLensDelay2 = Component(EpicsSignal, "2:interLensDelay", kind="config")

    #TODO gross motors
