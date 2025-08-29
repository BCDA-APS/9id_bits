import logging
import time as ttime
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Device
from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import ADComponent
from ophyd.areadetector.trigger_mixins import TriggerBase, ADTriggerStatus
from ophyd.status import wait as status_wait, SubscriptionStatus
from ophyd.device import Staged
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
    sg_trigger = FCpt(EpicsSignal, "{_sg_trigger}SG:plsTrn-1_Inp_Signal", labels={"area_detector","trigger"}, string=True)
    sg_upcntr_1_clear = FCpt(EpicsSignal, "{_sg_trigger}SG:UpCntr-1_CLEAR_Signal", labels={"area_detector","trigger"})
    sg_upcntr_2_clear = FCpt(EpicsSignal, "{_sg_trigger}SG:UpCntr-2_CLEAR_Signal", labels={"area_detector","trigger"})
    sg_trigger_disable = FCpt(EpicsSignal, "{_sg_trigger}SG:plsTrn-1_Dis_Signal", labels={"area_detector","trigger"})
    sg_upcntr_1_counts = FCpt(EpicsSignalRO, "{_sg_trigger}SG:UpCntr-1_COUNTS", labels={"area_detector","trigger"})
    sg_upcntr_2_counts = FCpt(EpicsSignalRO, "{_sg_trigger}SG:UpCntr-2_COUNTS", labels={"area_detector","trigger"})

class FastShutter(Device):

    def __init__(self, *args, fastShutterPV = None, image_name=None, **kwargs):
        if fastShutterPV is None:
            raise KeyError(f"Must define 'fastShutterPV': {kwargs=!r}")
        self._fast_shutter = fastShutterPV
        super().__init__(*args, **kwargs)

    fast_shutter_mode = FCpt(EpicsSignal, "{_fast_shutter}Lock", labels={"area_detector","fast shutter"})
    fast_shutter_actuate = FCpt(EpicsSignal, "{_fast_shutter}State", labels={"area_detector","fast shutter"})

    
class FancyTrigger(FastShutter, SoftglueTrigger, TriggerBase):
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
        self._array_count = self.cam.array_counter
        self._image_count = self.cam.num_images_counter
        self._ext_mode = 0 # 0 - count, 1 - motor scan
        self._num_frames = 0
        self._mod_frames = 10 
        self._delta = 0
        
        try:
            comp = getattr(self, 'hdf1')
        except AttributeError:
            self._hdf_on = "Disable"
        else:
            self._hdf_on = "Enable"
        
    def stage(self):
        super().stage()
        if self.cam.trigger_mode.get() == self._ext_trig_mode:          #   External Enable mode
            # Prep shutter
            # Put in Override
            self.fast_shutter_mode.put('0', wait=False)
            ttime.sleep(0.05) 
            # Open -- doesn't actually open, but puts in proper state 
            # for SG to open in Override mode
            self.fast_shutter_actuate.put('0', wait=False) 

            # Clear softglue counters
            self.sg_upcntr_1_clear.put('1!', wait = False)
            self.sg_upcntr_2_clear.put('1!', wait = False)
            # Clear AD array counter
            self.cam.array_counter.put(0)

            # Record counters for possible error checking
            self._original_read_attrs = self.read_attrs
            self.read_attrs = list(self.read_attrs) + ['sg_upcntr_2_counts', 'cam.array_counter']
            
            # Set Acquire to 1
            self._acquisition_signal.put(1, wait = True)

            # Get number of frames
            if self._trigger_control:               
                self._num_frames = self.cam.num_triggers.get()
            else:
                self._num_frames = self.cam.num_images.get()
                
            if self._ext_mode == 0:
                self._acquisition_signal.subscribe(self._acquire_changed)
            else:
                self._array_count.subscribe(self._count_changed)
        else:                               #   Presumably in internal series mode
            self._acquisition_signal.subscribe(self._acquire_changed)
            # Prep shutter
            self.fast_shutter_mode.put('1', wait=False)
            self.fast_shutter_actuate.put('0', wait=False)
        
        self._hdf_on = self.hdf1.enable.get()
        if self._hdf_on == 'Enable':
            self.hdf1.num_capture.put(self._num_frames)
            self.hdf1.capture.put(1)
        
        
    def abortSGtrigger(self):
        self.sg_trigger_disable.put("1", wait=False)
        ttime.sleep(0.05)
        self.sg_trigger_disable.put("0", wait=False)
        

    def unstage(self):
        while self.cam.acquire_busy.get():
            ttime.sleep(0.05)
                       
        if self._hdf_on  == 'Enable':
            self.hdf1.capture.put(0)

        self._acquisition_signal.clear_sub(self._acquire_changed)
       
        if self.cam.trigger_mode.get() == self._ext_trig_mode:          #   External Enable mode
            self.fast_shutter_mode.put('1', wait=False)
            ttime.sleep(0.05)
            self.fast_shutter_actuate.put('1', wait=False)
            self.cam.trigger_mode.put('0', wait=False)
            if self._ext_mode == 1:
                self._array_count.clear_sub(self._count_changed)
 #               self._image_count.clear_sub(self._count_changed)
        self.abortSGtrigger()
        
        self.read_attrs = self._original_read_attrs
        
        super().unstage()
        

    def trigger(self):
        '''
        Trigger one acquisition.
        '''
        if self._staged != Staged.yes:
            raise RuntimeError(
                "This detector is not ready to trigger."
                "Call the stage() method before triggering."
            )

        self._status = self._status_type(self)

        if self.cam.trigger_mode.get() == self._ext_trig_mode:          #   External Enable mode
            self.sg_trigger.put('1!', wait = False)
        else:                               #   Presumably in internal series mode
            self._acquisition_signal.put(1, wait=False)
        self.generate_datum(self._image_name, ttime.time(), {})
        return self._status

    def _acquire_changed(self, value=None, old_value=None, **kwargs):
        '''
        This is called when the 'acquire' signal changes.
        '''
        if self._status is None:
            return
        
        if (old_value == 1) and (value == 0):
            # Negative-going edge means an acquisition just finished.
            self._status.set_finished()
            self._status = None
                        
    def _count_changed(self, value=None, old_value=None, **kwargs):
        '''
        This is called when the image or array counter signal changes.
        '''
        if self._status is None:
            return
        if value > old_value:  # There is a new image!
            self._status.set_finished()
            self._status = None
    
    def prime_sg(self, 
        count : bool = False, 
        num_frames : int = None, 
        shutter_delay : float = None,
        on_time : float = None,
        period : float = None,
        mod_frames : int = 10
        ):
            
        '''
        Set up softglue for triggering eiger and sets eiger for 
        external triggers (External Enable)
        
        Parameters
        ==========

        count : bool = False
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

        mod_frames : int = 10, 
        For external enable mode and count plans, how often bluesky data is read in

        ''' 
        self.cam.trigger_mode.put(self._ext_trig_mode, wait = True)

        if num_frames is None:
            self._num_frames = self.cam.num_images.get()
        else:
            self._num_frames = num_frames
            self.cam.num_images.put(self._num_frames, wait = True)
        if self._trigger_control:               
            self.cam.num_triggers.put(self._num_frames, wait = True)

        if count:
            self._ext_mode = 0
            self._mod_frames = mod_frames
            self.sg_num_triggers.put(self._num_frames, wait = False)
        else:
            self._ext_mode = 1
            self.sg_num_triggers.put(1, wait = False)
        
                 
        # No equivalent AD component, so using only as an alternate to 
        # caQtDM for setting shutter delay
        if shutter_delay is None:
#           self.sg_shutter_delay.put(self.cam.shutter_delay.get(), wait = False)
            pass
        else:
#           self.sg_shutter_delay.put(shutter_delay, wait = False) 
            self.sg_shutter_delay.put(shutter_delay, wait = False) 
            
        if on_time is None:  
            on_time = self.cam.acquire_time.get()
        self.cam.acquire_time.put(on_time, wait = True)
        self.sg_on_time.put(on_time, wait = False)
        
                    
        if period is None:
            period = self.cam.acquire_period.get()
        if self._ext_mode == 0:
            self.cam.acquire_period.put(period, wait = True)
            self.sg_period.put(period, wait = False)    
        else:
            # Acquire period not necessary(?) for Eiger scans. Pilatus 
            # scans need Acquire Period > Acquire Time.Also, when period
            # is significantly longer than the exposure period (on_time)
            # then subsequent triggers are missed.
            if self._ext_trig_mode == 3: # Eiger
                self.cam.acquire_period.put(on_time, wait = True)
                self.sg_period.put(on_time, wait = False)          
            else:                       # Pilatus
                self.cam.acquire_period.put(on_time+0.01, wait = True)
                self.sg_period.put(on_time+0.01, wait = False)          

class FancyDetector(FancyTrigger, DetectorBase):
    """
    
    """
    def __init__(self, *args, ext_trig_mode=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if ext_trig_mode is None:
            print(f'FancyDetector external trigger mode not declared, defaulting to 1')
            self._ext_trig_mode = 1
        else:
            self._ext_trig_mode = int(ext_trig_mode)
            
        if self._ext_trig_mode == 3: # Eiger case
            self._trigger_control = True
        else:
            self._trigger_control = False
        
    def save_hdf1_on(self, 
                    fname : str = None, 
                    fnumber : int = None, 
                    fpath : str = None
                    ):
                        
        def check_value(*, old_value, value, **kwargs):
            '''
            Return True when hdf1 is enabled"
            '''
            return value == "Enable"

        if fpath is not None:
            self.hdf1.file_path.put(fpath)

        if fname is not None:
            self.hdf1.file_name.put(fname)

        if fnumber is not None:
            self.hdf1.file_number.put(fnumber)


        if self.hdf1.enable.get() != "Enable":
            self.hdf1.enable.put("Enable")
            status_wait(
                SubscriptionStatus(self.hdf1.enable, check_value, timeout=10)
            )

    def save_hdf1_off(self):
        def check_value(*, old_value, value, **kwargs):
            '''
            Return True when hdf1 is disabled"
            '''
            return value == "Disable"

        if self.hdf1.enable.get() != "Disable":
            self.hdf1.enable.put("Disable")
            status_wait(
                SubscriptionStatus(self.hdf1.enable, check_value, timeout=10)
            )

    
