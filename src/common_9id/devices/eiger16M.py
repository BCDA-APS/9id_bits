import logging

from apstools.devices.area_detector_support import CamMixin_V34
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import ADComponent
from ophyd.areadetector import CamBase, EigerDetectorCam
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector.base import EpicsSignalWithRBV as SignalWithRBV
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.areadetector.detectors import DetectorBase

logger = logging.getLogger(__name__)
logger.info(__file__)

class SoftglueTrigger(Device):
    
    def __init__(self, *args, sg_trigger = None, image_name=None, **kwargs):
        if sg_trigger is None:
            sg_trigger = "cam1:".join([self.prefix, "Trigger"])
        self._sg_trigger = sg_trigger
        super().__init__(*args, **kwargs)
        
    # This won't work if sg_trigger defaults to cam's Trigger -- need to rethink
    sg_on_time = FCpt(EpicsSignal, "{_sg_trigger}userTran1.C", labels={"area_detector","trigger"})
    sg_period = FCpt(EpicsSignal, "{_sg_trigger}userTran1.A", labels={"area_detector","trigger"})
    sg_shutter_delay = FCpt(EpicsSignal, "{_sg_trigger}userTran1.E", labels={"area_detector","trigger"})
    sg_num_triggers = FCpt(EpicsSignal, "{_sg_trigger}userTran1.J", labels={"area_detector","trigger"})
    sg_trigger = FCpt(EpicsSignal, "{_sg_trigger}SG:plsTrn-1_Inp_Signal", labels={"area_detector","trigger"})


class FancyTrigger(SoftglueTrigger, TriggerBase):
    """
    TODO: Update to handle Eiger's Multiple Enable w/ + w/o motors along
    with internal series (though Multiple Enable w/o motors may replace
    internal series for alignment tasks as it handles shutter better)
    
    In Mulitple Enable + motors:
        SG trigger count = 1
        AD NumImage = # of motor points
        Acquire set during staging?
        trigger fxn calls SG trigger (set to "1!"
        
    In Multiple Enable w/o motors:
        SG trigger count = AD NumImage
        Acquire set during staging?
        trigger fxn calls SG trigger (set to "1!"
        
    
    """
    _status_type = ADTriggerStatus
    
    def __init__(self, *args, image_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        if image_name is None:
            image_name = "_".join([self.name, "image"])
        self._image_name = image_name
        self._image_count = self.cam.num_images_counter
        self._ext_mode = 0
        try:
            comp = getattr(self, 'hdf1')
        except AttributeError:
            self._hdf_on = False
        else:
            self._hdf_on = True
        
    def stage(self):
        if self.trigger_mode == 3:          #   External Enable mode
            # Set Acquire to 1
            self._acquisition_signal.put(1, wait = False)
            # TODO what signal to subscribe to check if acquire is complete?
            self._image_count.subscribe(self._image_count_changed)
            self._total_images = int(self.sg_num_triggers.get())
        else:                               #   Presumably in internal series mode
            self._acquisition_signal.subscribe(self._acquire_changed)
        
        self._hdf_on = self.hdf1.enable.get()
        if self._hdf_on:
            self.hdf1.capture.put(1)
        
        super().stage()


    def unstage(self):
        super().unstage()
        
        if self._hdf_on:
            self.hdf1.capture.put(0)
       
        if self.trigger_mode == 3:          #   External Enable mode
            self._image_count.clear_sub(self._image_count_changed)
        else:                               #   Presumably in internal series mode
            self._acquisition_signal.clear_sub(self._acquire_changed)

    def trigger(self):
        "Trigger one acquisition."
        if self._staged != Staged.yes:
            raise RuntimeError(
                "This detector is not ready to trigger."
                "Call the stage() method before triggering."
            )

        self._status = self._status_type(self)

        if self.trigger_mode == 3:          #   External Enable mode
            self.sg_trigger.put('1!', wait = False)
        else:                               #   Presumably in internal series mode
            self._acquisition_signal.put(1, wait=False)

        self.generate_datum(self._image_name, ttime.time(), {})
        return self._status

    def _acquire_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        
        if (old_value == 1) and (value == 0):
            # Negative-going edge means an acquisition just finished.
            self._status.set_finished()
            self._status = None
                        
    def _image_count_changed(self, value=None, old_value=None, **kwargs):
        "This is called when the 'acquire' signal changes."
        if self._status is None:
            return
        if value > self._total_images:  # There is a new image!
            self._status.set_finished()
            self._status = None
    
    def prime_sg(self, 
        count : bool = True, 
        num_frames : int = None, 
        shutter_delay : float = None,
        on_time : float = None,
        period : float = None
        ):
            
        '''
        Set up softglue for triggering eiger 
        
        Parameters
        ==========

        count : bool = True
        set to true if count plan to be run otherwise set to false 
        
        num_frames : int = None, 
        Number of frames at each point; for motor scan set to num of steps 
        in scan; for count set to total number of images desired. By default 
        will get from AD NumImage_RBV
        
        shutter_delay : float = None,
        Shutter delay in seconds
        
        on_time : float = None,
        Exposure time in seconds. If not set, will get from AD's Acquire Time
        
        period : float = None
        Acquire period (>= exposure time) in seconds.  If not set, will get
        from AD Acquire Period

        ''' 
    
        if count:
            if num_frames is None:
                self.sg_num_triggers.put(self.cam.num_images.get(), wait = False)
            else:
                self.sg_num_triggers.put(num_frames, wait = False)
                self.cam.num_images.put(num_frames, wait = False)
        else:
            self.sg_num_triggers.put(1, wait = False)
            if num_frames is not None:
                self.cam.num_images.put(num_frames, wait = False)
                
        # No equivalent AD component, so using only as an alternate to 
        # caQtDM for setting shutter delay
        if shutter_delay is None:
#           self.sg_shutter_delay.put(self.cam.shutter_delay.get(), wait = False)
            pass
        else:
#           self.sg_shutter_delay.put(shutter_delay, wait = False) 
            self.sg_shutter_delay.put(shutter_delay, wait = False) 
            
        if on_time is None:
            self.sg_on_time.put(self.cam.acquire_time.get(), wait = False)
        else:
            self.cam.acquire_time.put(on_time, wait = False)
            self.sg_on_time.put(on_time, wait = False)
                    
        if period is None:
            self.sg_period.put(self.cam.acquire_period.get(), wait = False)
        else:
            self.cam.acquire_period.put(period, wait = False)
            self.sg_period.put(period, wait = False)
          

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
            "Return True when file writer is enabled"
            return value == "ready"

        self.cam.fw_enable.put("Enable")
        status_wait(
            SubscriptionStatus(self.cam.fw_state, check_value, timeout=10)
        )

    def save_images_off(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writer is disabled"
            return value == "disabled"

        self.cam.fw_enable.put("Disable")
        status_wait(
            SubscriptionStatus(self.hdf1, check_value, timeout=10)
        )


class FancyEigerDetector(FancyTrigger, DetectorBase):
    """
    
    """
    def save_hdf1_on(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writer is enabled"
            return value == "Enable"

        self.hdf1.enable.put("Enable")
        status_wait(
            SubscriptionStatus(self.hdf1.enable, check_value, timeout=10)
        )

    def save_hdf1_off(self):
        def check_value(*, old_value, value, **kwargs):
            "Return True when file writer is disabled"
            return value == "Disable"

        self.hdf1.enable.put("Disable")
        status_wait(
            SubscriptionStatus(self.hdf1.enable, check_value, timeout=10)
        )
    

class BadPixelPlugin(PluginBase):
    """
    ADCore NDBadPixel, new in AD 3.13.

    (new in apstools release 1.7.3)
    """
    _html_docs = ["NDBadPixelDoc.html"]
    
    file_name = ADComponent(EpicsSignal, "FileName", string=True)


