"""
1. Omega Mass Flow controller as stream device

2. Omega Mass Flow controller over asyn record

    Usage
    
    # set flow rate to 1.7:
    omega_mfc.put(1.7)
    
    # get current readback: 
    readback = omega_mfc.get()

"""

import logging
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from apstools.synApps.asyn import AsynRecord

import time as ttime

import re   



logger = logging.getLogger(__name__)
logger.info(__file__)

class omegaMFCstream(Device):
    '''
    
    '''

    flow_setpoint = Cpt(EpicsSignal, "flowSP_RBV", write_pv = "flowSP", kind="hinted")

    pressure = Cpt(EpicsSignalRO, "pressure_RBV", kind="hinted")
    temperature = Cpt(EpicsSignalRO, "temp_RBV", kind="hinted")
    vol_flow = Cpt(EpicsSignalRO, "volFlow_RBV", kind="hinted")
    mass_flow = Cpt(EpicsSignalRO, "massFlow_RBV", kind="hinted")
    gas = Cpt(EpicsSignalRO, "gas_RBV", string=True, kind="hinted")




SET_COMMAND_STR = 'AS'
READ_COMMAND_STR = 'A'

class omegaMFCasyn(Device, AsynRecord):
    '''

    '''
    def __init__(self, 
                 prefix: str,
                 *args,
                 **kwargs,
                ):
                
        super().__init__(prefix, *args, **kwargs)
    
    
    def put(self, value,  *args, **kwargs):
        comm_str = SET_COMMAND_STR
        
        value = f"{comm_str:s}{value:2.1f}"
        self.ascii_ouput.put(self, value, *args, **kwargs)
    
    def get(self, *args, **kwargs):
        
        self.ascii_output.put(self, READ_COMMAND_STR, *args, **kwargs)
    
        string_value = self.translated_input.get(self, *args, **kwargs)
        
        pattern = r"[-+]?\d*\.?\d+"
        match = re.search(pattern, string_value)
    
        if not match:
            # raise error?
            print("No float found in the string.")        
        else:
            value_str = match.group(0)  # Get the matched string
            value = float(value_str) # Convert to actual float
            return value
    

        
        
        
        
    
    
    
    
    
