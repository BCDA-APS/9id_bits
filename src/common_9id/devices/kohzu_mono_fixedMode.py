"""
KohzuSeqCtl_Mono_FixedMode locks the mode of the KohzuSeqCtl_Monochromator
    
"""

from ophyd import Component
from ophyd import EpicsSignal, EpicsSignalRO
from apstools.devices import KohzuSeqCtl_Monochromator

class KohzuSeqCtl_Mono_FixedMode(KohzuSeqCtl_Monochromator):
	"""
    synApps Kohzu double-crystal monochromator with mode fixed (locked by
    EPICS security control)

    """
	mode = Component(EpicsSignalRO, "KohzuModeBO", kind="config", string=True)

