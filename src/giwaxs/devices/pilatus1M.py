from apstools.devices.area_detector_support import CamMixin_V34
from ophyd import ADComponent
from ophyd.areadetector import PilatusDetectorCam
from ophyd import EpicsSignal

class PilatusDetectorCam_V34(CamMixin_V34, PilatusDetectorCam):
    """Adds triggering configuration and AcquireBusy support."""

    nd_attr_status = ADComponent(
        EpicsSignal,
        "NDAttributesStatus",
        kind="omitted",
        string=True,
    )
