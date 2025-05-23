"""
Alignment plans for 9ID
=====================

For development and testing only, provides plans.

.. autosummary::
    ~center_and_parallelize
"""

import logging

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from blueksy import plan_patterns

try:
    # cytools is a drop-in replacement for toolz, implemented in Cython
    from cytools import partition
except ImportError:
    from toolz import partition

from apsbits.utils.controls_setup import oregistry

logger = logging.getLogger(__name__)
logger.bsdev(__file__)

#DEFAULT_MD = {"title": "test run with simulator(s)"}



# need to expand mover for translation and pitch motors -- is this the right way? Should look at scan_2d or grid_scan..
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


