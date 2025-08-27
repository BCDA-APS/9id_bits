import logging
import time as ttime
from apstools.devices.area_detector_support import CamMixin_V34
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import ADComponent
from ophyd.areadetector import CamBase, EigerDetectorCam
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector.base import EpicsSignalWithRBV as SignalWithRBV
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.areadetector.detectors import DetectorBase
from ophyd.device import Staged

from .fancyTriggers import FancyDetector

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

class Eiger2DetectorCam_V34(CamMixin_V34, EigerDetectorCam):
    """Adds triggering configuration and AcquireBusy support.
    
       Replaces Threshhold energy with Threshold Energy1 and Threshold 
       Enery2
    
    """
    _default_configuration_attrs = CamBase._default_configuration_attrs + (
        "shutter_mode",
        "num_triggers",
        "beam_center_x",
        "beam_center_y",
        "wavelength",
        "det_distance",
        "threshold1_energy",
        "threshold2_energy",
        "photon_energy",
        "manual_trigger",
        "special_trigger_button",
    )
    
    initialize = ADComponent(EpicsSignal, "Initialize", kind="config")
    
    threshold_energy = None
    threshold1_energy = ADComponent(SignalWithRBV, "ThresholdEnergy")
    threshold2_energy = ADComponent(SignalWithRBV, "Threshold2Energy")

    nd_attr_status = ADComponent(
        EpicsSignal,
        "NDAttributesStatus",
        kind="omitted",
        string=True,
    )

    def save_images_on(self):
        def check_value(*, old_value, value, **kwargs):
            '''
            Return True when file writer is enabled
            '''
            return value == "ready"

        if self.cam.fw_enable.get() != 1:
            self.cam.fw_enable.put("Enable")
            status_wait(
                SubscriptionStatus(self.cam.fw_state, check_value, timeout=10)
            )

    def save_images_off(self):
        def check_value(*, old_value, value, **kwargs):
            '''
            Return True when file writer is disabled
            '''
            return value == "disabled"

        if self.cam.fw_enable.get() != 0:
            self.cam.fw_enable.put("Disable")
            status_wait(
                SubscriptionStatus(self.hdf1, check_value, timeout=10)
            )


class FancyEigerDetector(FancyDetector):
    """
    
    """
    pass
    

class BadPixelPlugin(PluginBase):
    """
    ADCore NDBadPixel, new in AD 3.13.

    (new in apstools release 1.7.3)
    """
    _html_docs = ["NDBadPixelDoc.html"]
    
    file_name = ADComponent(EpicsSignal, "FileName", string=True)


