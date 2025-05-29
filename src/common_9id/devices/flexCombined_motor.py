import logging

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import FormattedComponent as FCpt
from ophyd import EpicsMotor
from ophyd import EpicsSignal, EpicsSignalRO

logger = logging.getLogger(__name__)
logger.info(__file__)

class FlexCombined(Device):
    """
    Flex Combined motors consist of 3 motors (combined, fine, and coarse)
    and a cap sensor (or encoder) for overall position.
    
    flexCominedMotion is part of synApps's optics module

    Parameters
    ==========
    combined:
      The motor record PV controlling the combined pseudo motor, ex "9ida:CR9A1:m3"
    fine:
      The motor record PV controlling the real fine motor, ex "9ida:CR9A1:m4"
    coarse:
      The motor record PV controlling the real coarse motor, ex: "9ida:CR9A1:m1"
    cap_sensor:
      The PV of the position readback, ex: "9ida:CR9A1:m2"
    """

    def __init__(
        self,
        prefix: str,
        combined: str,
        fine: str,
        coarse: str,
        *args,
        **kwargs,
    ):
#        # Determine the prefix for the motors
#        pieces = prefix.strip(":").split(":")
#        self.motor_prefix = ":".join(pieces[:-1])

        self._combined = combined
        self._fine = fine
        self._coarse = coarse

        super().__init__(prefix, *args, **kwargs)


    combined = FCpt(EpicsMotor, "{_combined}", labels={"motors"})
    # Real motors that when combined produce the total motion
    fine = FCpt(EpicsMotor, "{_fine}", labels={"motors"})
    coarse = FCpt(EpicsMotor, "{_coarse}", labels={"motors"})


    mode = FCpt(EpicsSignal, "{_combined}:mode", kind="config")
    rehomed = FCpt(EpicsSignalRO, "{_combined}:rehome", kind="config")
    piezoUpperLimit = FCpt(EpicsSignal, "{_combined}:upperLimit", kind="config")
    piezoLowerLimit = FCpt(EpicsSignal, "{_combined}:lowerLimit", kind="config")
    piezoHomePos = FCpt(EpicsSignal, "{_combined}:homePos", kind="config")
    


class FlexCombinedCap(FlexCombined):
    """
    Flex Combined Cap motors consist of 3 motors (combined, fine, and coarse)
    and a cap sensor for overall position.
    

    Parameters
    ==========
    combined:
      The motor record PV controlling the combined pseudo motor, ex "9ida:CR9A1:m3"
    fine:
      The motor record PV controlling the real fine motor, ex "9ida:CR9A1:m4"
    coarse:
      The motor record PV controlling the real coarse motor, ex: "9ida:CR9A1:m1"
    cap_sensor:
      The PV of the position readback, ex: "9ida:CSSI:cap0"
    """

    def __init__(
        self,
        prefix: str,
        cap_sensor: str,
        *args,
        **kwargs,
    ):
        
        self._cap_sensor = cap_sensor

        super().__init__(prefix, *args, **kwargs)

    class capSensor(Device):
        def __init__(
            self,
            prefix,
            *args,
            **kwargs,
        ):           

            super().__init__(prefix, *args, **kwargs)
            
        voltage = Cpt(EpicsSignalRO, "voltage")
        pos = Cpt(EpicsSignalRO, "pos")
        umPerV = Cpt(EpicsSignalRO, "umPerV")
        offset = Cpt(EpicsSignal, "offset")
        
    cap = FCpt(capSensor, "{prefix}{_cap_sensor}:", labels={"sensor"})

class FlexCombinedEnc(FlexCombined):
    """
    Flex Combined Enc motors consist of 3 motors (combined, fine, and coarse)
    and an encoder for overall position.
    
    Parameters
    ==========
    combined:
      The motor record PV controlling the combined pseudo motor, ex "9ida:CR9A1:m3"
    fine:
      The motor record PV controlling the real fine motor, ex "9ida:CR9A1:m4"
    coarse:
      The motor record PV controlling the real coarse motor, ex: "9ida:CR9A1:m1"
    enc_sensor:
      The PV of the position readback, ex: "9ida:CSSI:enc1"
    """

    def __init__(
        self,
        prefix: str,
        enc_sensor: str,
        *args,
        **kwargs,
    ):
        
        self._enc_sensor = enc_sensor

        super().__init__(prefix, *args, **kwargs)

    class encSensor(Device):

        pos = Cpt(EpicsSignalRO, "pos")

        
    enc = FCpt(encSensor, "{prefix}{_enc_sensor}:", labels={"sensor"})
