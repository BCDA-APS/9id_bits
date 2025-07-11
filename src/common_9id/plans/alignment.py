"""
Alignment plans for 9ID
=====================

For development and testing only, provides plans.

.. autosummary::
    ~edge_align_ad
    ~center_and_parallelize
"""

import datetime
import logging
import sys

import numpy as np
import pyRestTable
from scipy.optimize import curve_fit
from scipy.special import erf

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from blueksy import plan_patterns
from bluesky import preprocessors as bpp
from bluesky.callbacks.fitting import PeakStats
from ophyd import Component
from ophyd import Device
from ophyd import Signal
from ophyd.scaler import ScalerCH
from ophyd.scaler import ScalerChannel

from apstools import utils
from apstools.plans.doc_run import write_stream

from ..devices.adplugin_support import prepare_STATS

try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytools import partition
except ImportError:
    from toolz import partition

from apsbits.utils.controls_setup import oregistry

logger = logging.getLogger(__name__)
logger.bsdev(__file__)
# This was from original edge_align/alignment.py from apstools
# MAIN = sys.modules["__main__"]

def edge_align_ad(detectors, mover, start, end, points, adplugin = {"stats_n" : 1, "stat": "total"}, cat=None, md={}):
    """
    Align to the edge given mover & detector data, relative to absolute position.

    This plan can be used in the queueserver, Jupyter notebooks, and IPython
    consoles.

    PARAMETERS
    ----------
    detectors *Readable* or [*Readable*]:
        Detector object or list of detector objects (each is a Device or
        Signal).

    mover *Movable*:
        Mover object, such as motor or other positioner.

    start *float*:
        Starting point for the scan. This is an absolute motor location.

    end *float*:
        Ending point for the scan. This is an absolute motor location.

    points *int*:
        Number of points in the scan.

   adplugin *dict*:
        Which stats plugin/signal to use in matching erf to

    cat *databroker.temp().v2*:
        Catalog where bluesky data is saved and can be retrieved from.

    md *dict*:
        User-supplied metadata for this scan.
    """

    def guess_erf_params(x_data, y_data):
        """
        Provide an initial guess for the parameters of an error function.

        Parameters
        ----------
        x_data : A numpy array of the values on the x_axis
        y_data : A numpy array of the values on the y_axis

        Returns
        -------
        guess : dict
            A dictionary containing the guessed parameters 'low_y_data', 'high_y_data', 'width', and 'midpoint'.
        """

        # Sort data to make finding the mid-point easier and to assist in other estimations
        y_data_sorted = np.sort(y_data)
        x_data_sorted = np.sort(x_data)

        # Estimate low and high as the first and last elements (assuming sorted data)
        low_y_data = np.min(y_data_sorted)
        high_y_data = np.max(y_data_sorted)

        low_x_data = np.min(x_data_sorted)
        high_x_data = np.max(x_data_sorted)

        # Estimate width as a fraction of the range. This is very arbitrary and might need tuning!
        # This is a guess and might need adjustment based on your data's characteristics.
        width = (high_x_data - low_x_data) / 10

        # Estimate the midpoint of the x values
        midpoint = x_data[int(len(x_data) / 2)]

        return [low_y_data, high_y_data, width, midpoint]

    def erf_model(x, low, high, width, midpoint):
        """
        Create error function for fitting and simulation

        Parameters
        ----------
        x       :   input upon which error function is evaluated
        low     :   min value of error function
        high    :   max value of error function
        width   :   "spread" of error function transition region
        midpoint:   location of error function's "center"
        """
        return (high - low) * 0.5 * (1 - erf((x - midpoint) / width)) + low

    if not isinstance(detectors, (tuple, list)):
        detectors = [detectors]

    if not isinstance(adplugin["stat"], (tuple, list)):
        adplugin["stat"] = [adplugin["stat"]]


    _md = dict(purpose="edge_align")
    _md.update(md or {})

    prepare_STATS(detectors[0], STATS_num=adplugin["stats_n"], BEC=adplugin["stat"], read_attrs=adplugin["stat"])

    uid = yield from bp.scan(detectors, mover, start, end, points, md=_md)
    cat = cat or utils.getCatalog()
    run = cat[uid]  # return uids
    ds = run.primary.read()

    x = ds[mover.name]
    y_signal_name = detectors[0].name+'_stats'+str(adplugin["stats_n"])+'_'+adplugin["stat"][0]
    y = ds[y_signal_name]

    try:
        initial_guess = guess_erf_params(x, y)
        popt, pcov = curve_fit(erf_model, x, y, p0=initial_guess)
        if pcov[3, 3] != np.inf:
            print("Significant signal change detected; motor moving to detected edge.")
            yield from bps.mv(mover, popt[3])
        else:
            raise Exception
    except Exception as reason:
        print(f"reason: {reason}")
        print("No significant signal change detected; motor movement skipped.")






#DEFAULT_MD = {"title": "test run with simulator(s)"}
# TODO need to expand mover for translation and pitch motors -- is this the right way? Should look at scan_2d or grid_scan..
def center_and_parallel(    
	detectors: Sequence[Readable],
    *args,
    snake_axes: Optional[Union[Iterable, bool]] = None,
    per_step: Optional[PerStep] = None,
    md: Optional[CustomPlanMetadata] = None,
) -> MsgGenerator[str]:
	"""
	1. Translate until 1/2 intensity (apstools.plans.edge_align)
	2. Rotate until max intensity (or midpoint of max intensity)
	3. Translate (again) until 1/2 intensity (apstools.plans.edge_align)

    PARAMETERS
    ----------
     detectors: list or tuple
        list of 'readable' objects
    ``*args``
        patterned like (``motor1, start1, stop1, num1,``
                        ``motor2, start2, stop2, num2``)
        The first motor is the centering motor, and the second motor
        is the pitch motor -- for rotating sample parallel to beam.
    snake_axes: boolean or iterable, optional
        which axes should be snaked, either ``False`` (do not snake any axes),
        ``True`` (snake all axes) or a list of axes to snake. "Snaking" an axis
        is defined as following snake-like, winding trajectory instead of a
        simple left-to-right trajectory. The elements of the list are motors
        that are listed in `args`. The list must not contain the slowest
        (first) motor, since it can't be snaked.
    per_step: callable, optional
        hook for customizing action of inner loop (messages per step).
        See docstring of :func:`bluesky.plan_stubs.one_nd_step` (the default)
        for details.
    md: dict, optional
        metadata

    See Also
    --------
    :func:`bluesky.plans.grid_scan`
	"""
	# Taken from bp.grid_scan
    args_pattern = plan_patterns.classify_outer_product_args_pattern(args)
    if (snake_axes is not None) and (args_pattern == plan_patterns.OuterProductArgsPattern.PATTERN_2):
        raise ValueError(
            "Mixing of deprecated and new API interface is not allowed: "
            "the parameter 'snake_axes' can not be used if snaking is "
            "set as part of 'args'"
        )

	# Taken from bp.grid_scan
    chunk_args = list(plan_patterns.chunk_outer_product_args(args, args_pattern))
    # 'chunk_args' is a list of tuples of the form: (motor, start, stop, num, snake)
    # If the function is called using deprecated pattern for arguments, then
    # 'snake' may be set True for some motors, otherwise the 'snake' is always False.

    # The list of controlled motors
    motors = [_[0] for _ in chunk_args]

    # Check that the same motor is not listed multiple times. This indicates an error in the script.
    if len(set(motors)) != len(motors):
        raise ValueError(f"Some motors are listed multiple times in the argument list 'args': '{motors}'")
    # Check that two distinct motors were provided. This indicates an error in the script.
    if len(motors) != 2:
		raise ValueError(f"center_and_parallelize requires 2 distinct motors. '{len(motors)}' motors were provided")

  # TODO -- rethink this (look at scan, grid_scan for other examples)
  # set some variables and check that all lists are the same length
    lengths = {}
    motors: list[Any] = []
    pos_lists = []
    length = None
    for motor, pos_list in partition(2, args):
        pos_list = list(pos_list)  # Ensure list (accepts any finite iterable).
        lengths[motor.name] = len(pos_list)
        if not length:
            length = len(pos_list)
        motors.append(motor)
        pos_lists.append(pos_list)
    length_check = all(elem == list(lengths.values())[0] for elem in list(lengths.values()))

    if not length_check:
        raise ValueError(
            f"The lengths of all lists in *args must be the same. However the lengths in args are : {lengths}"
        )



	yield from edge_align(detectors, motors[0], start_pos[0], end_pos[0], pnts[0], cat=None, md={})
#	yield from parallelize(detectors, mover_pitch, start_pitch, end_pitch, points_pitch, cat=None, md={})
	yield from bp.tune_centroid(detectors, motors[1] start_pos[1], end_pos[1], pnt[1], cat=None, md={})

	yield from edge_align(detectors, motors[0], start_pos[0], end_pos[0], pnts[0], cat=None, md={})


