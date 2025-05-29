import logging

from apstools.devices.area_detector_support import CamMixin_V34
from ophyd import ADComponent
from ophyd.areadetector import EigerDetectorCam
from ophyd import EpicsSignal
from ophyd.areadetector.plugins import PluginBase

logger = logging.getLogger(__name__)
logger.info(__file__)


class EigerDetectorCam_V34(CamMixin_V34, EigerDetectorCam):
    """Adds triggering configuration and AcquireBusy support."""

    nd_attr_status = ADComponent(
        EpicsSignal,
        "NDAttributesStatus",
        kind="omitted",
        string=True,
    )

class BadPixelPlugin(PluginBase):
    """
    ADCore NDBadPixel, new in AD 3.13.

    (new in apstools release 1.7.3)
    """
    _html_docs = ["NDBadPixelDoc.html"]
    
    file_name = ADComponent(EpicsSignal, "FileName", string=True)
