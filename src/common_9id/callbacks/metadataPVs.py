"""
custom callbacks
================

.. autosummary::
    :nosignatures:

    ~metadataPV_start_preprocessor
    ~baseline_start_preprocessor
    ~baseline_end_preprocessor
"""

from apstools.plans import label_stream_wrapper

def metadataPV_start_preprocessor(plan):

    return label_stream_wrapper(plan, "metadataPV", when="start")

def baseline_start_preprocessor(plan):
    
    return label_stream_wrapper(plan, "baseline", when="start")

def baseline_end_preprocessor(plan):
    
    return label_stream_wrapper(plan, "baseline", when="end")
