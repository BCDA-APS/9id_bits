"""
custom callbacks
================

.. autosummary::
    :nosignatures:

    ~metadataPV_start_preprocessor
"""

from apstools.plans import label_stream_wrapper

def metadataPV_start_preprocessor(plan):

    return label_stream_wrapper(plan, "metadataPV", when="start")

