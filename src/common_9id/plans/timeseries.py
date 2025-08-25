"""
Alignment plans for 9ID
=====================

For development and testing only, provides plans.

.. autosummary::
    ~ext_trig_ts
"""
import logging

from apsbits.utils.controls_setup import oregistry

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

from bluesky.preprocessors import monitor_during_wrapper
from bluesky.callbacks import LiveTable, LivePlot
from bluesky.plans import count
from bluesky.preprocessors import subs_decorator

SG_DEFAULTS = {'count'          : True,
               'num_frames'     : None,
               'shutter_delay'  : None,
               'on_time'        : None,
               'period'         : None,
               'mod_frames'     : 10
               }

def ext_trig_ts(detector, 
        monitor,         
        num_frames : int = None, 
        shutter_delay : float = None,
        on_time : float = None,
        period : float = None,
        mod_frames : int = 10,
        hdf  : bool = False, 
        mPlot : bool = True, 
        mTable : bool = True, 
        md = {}):
    """
    External trigger timeseries -- sets up soft glue triggering/shutter 
    behavior and monitors signals for a count plan

    PARAMETERS
    ----------
    detector *Readable* or [*Readable*]:
        Detector object or list of detector objects (each is a Device or
        Signal).

    monitor *Readable* or [*Readable*]:
        Detector object or list of detector objects (each is a Device or
        Signal) to be monitored asynchronously
        
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

    hdf *bool*:

    mPlot *bool*:

    mTable *bool*:

    md *dict*:
        User-supplied metadata for this scan.
    """
    if not isinstance(detector, list):
        detector = [detector] 

    for det in detector:
        det.prime_sg(count = True, 
                     num_frames = num_frames, 
                     shutter_delay = shutter_delay,
                     on_time = on_time, 
                     period = period,
                     mod_frames = mod_frames)
        if hdf:
            det.save_hdf1_on()
        else:
            det.save_hdf1_off()

    if not isinstance(monitor, list):
        monitor = [monitor]
    
    monitor_cbs_list = []
    for m in monitor:
        nm = m.name
        if mPlot: monitor_cbs_list.append(LivePlot(nm))
        monitor_cbs_list.append(LiveTable([m], stream_name=nm+'_monitor'))
    monitor_cbs_tuple = tuple(monitor_cbs_list)

    @subs_decorator(monitor_cbs_tuple)
    def inner():
        yield from monitor_during_wrapper(count(detector), monitor)
            
    yield from inner()
    
"""
Old commands:   
monitor_table = LiveTable([eiger16m.stats4.total], stream_name = 'eiger16m_stats4_total_monitor')
monitor_plot = LivePlot('eiger16m_stats4_total')
re_subscriptions = unsubscribe_bec(RE, re_subscriptions)
eiger16m.prime_sg(num_frames = 5, shutter_delay = 0.05, on_time = 1.2, period = 1.5)
RE(monitor_during_wrapper(bp.count([eiger16m]),[eiger16m.stats4.total]), (monitor_plot, monitor_table))


New commands:
re_subscriptions = unsubscribe_bec(RE, re_subscriptions)
RE(ext_trig_ts(eiger16m, eiger16m.stats4.total)

And if BEC wanted again after experiment
re_subscriptions = subscribe_bec(RE, re_subscriptions)

"""
