from apstools.devices.area_detector_support import CamMixin_V34
from ophyd import ADComponent
from ophyd.areadetector import EigerDetectorCam
from ophyd import EpicsSignal

class EigerDetectorCam_V34(CamMixin_V34, EigerDetectorCam):
    """Adds triggering configuration and AcquireBusy support."""

    nd_attr_status = ADComponent(
        EpicsSignal,
        "NDAttributesStatus",
        kind="omitted",
        string=True,
    )
