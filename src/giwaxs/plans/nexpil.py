"""
Simple, modular Bluesky plans for users.
"""

""" for 8ID
from apsbits.core.instrument_init import oregistry
at 9ID:
"""
from apsbits.utils.controls_setup import oregistry
from bluesky import plan_stubs as bps
from bluesky import plans as bp

""" for 8ID
from ..utils.dm_util import dm_run_job
from ..utils.dm_util import dm_setup
from ..utils.nexus_utils import create_nexus_format_metadata
from .sample_info_unpack import gen_folder_prefix
from .sample_info_unpack import mesh_grid_move
from .shutter_logic import blockbeam
from .shutter_logic import post_align
from .shutter_logic import showbeam
from .shutter_logic import shutteroff
"""
pilatus1m = oregistry["pilatus1m"]
"""
pv_registers = oregistry["pv_registers"]
"""

pv_registers = oregistry["registers"]

def setup_pilatus_int_series(acq_time, num_frames, file_name):
    """Setup the Eiger4M for internal series acquisition.

    Configure the detector's cam module for internal acquisition mode and
    set up the HDF plugin for data storage.

    Args:
        acq_time: Acquisition time per frame in seconds
        num_frames: Number of frames to acquire
        file_name: Base name for the output files
    """
    cycle_name = pv_registers.cycle_name.get()
    exp_name = pv_registers.experiment_name.get()

    file_path = f"/gdata/dm/8ID/8IDI/{cycle_name}/{exp_name}/data/{file_name}"

    acq_period = acq_time
    yield from bps.mv(pilatus1m.cam.trigger_mode, "Internal Series")  # 0
    yield from bps.mv(pilatus1m.cam.acquire_time, acq_time)
    yield from bps.mv(pilatus1m.cam.acquire_period, acq_period)
    yield from bps.mv(pilatus1m.hdf1.file_name, file_name)
    yield from bps.mv(pilatus1m.hdf1.file_path, file_path)
    yield from bps.mv(pilatus1m.cam.num_images, num_frames)
    yield from bps.mv(
        pilatus1m.cam.num_triggers, 1
    )  # Need to put num_trigger to 1 for internal mode
    yield from bps.mv(pilatus1m.hdf1.num_capture, num_frames)

    yield from bps.mv(pv_registers.file_name, file_name)
    yield from bps.mv(pv_registers.file_path, file_path)
    yield from bps.mv(
        pv_registers.metadata_full_path, f"{file_path}/{file_name}_metadata.hdf"
    )

############# Homebrew acquisition plan #############
def pilatus_acquire():

    yield from showbeam()
    yield from bps.sleep(0.1)
    yield from bps.mv(pilatus1m.hdf1.capture, 1)
    yield from bps.mv(pilatus1m.cam.acquire, 1)
        
    while True:
        det_status = pilatus1m.cam.acquire_busy.get()
        if det_status == 1:
            yield from bps.sleep(0.1)
        if det_status == 0:
            break
    yield from blockbeam()

    frame_num_set = pilatus1m.hdf1.queue_size.get()
    count = 0
    while count < 100:
        frame_num_processed = pilatus1m.hdf1.queue_free.get()
        if frame_num_processed == frame_num_set:
            break
        else:
            yield from bps.sleep(0.1)
            count=+1
        pilatus1m.hdf1.capture.put(0)
############# Homebrew acquisition plan ends #############


def pilatus_acq_int_series(
    acq_time=1,
    num_frames=10,
    num_rep=3,
    wait_time=0,
    process=True,
    sample_move=False,
):
    """Run internal series acquisition with the Eiger detector.

    Args:
        acq_time: Acquisition time per frame in seconds
        num_frames: Number of frames to acquire
        num_rep: Number of repetitions
        wait_time: Time to wait between repetitions
        process: Whether to process data after acquisition
        sample_move: Whether to move sample between repetitions
    """
    # try:
    yield from post_align()
    yield from shutteroff()
    workflowProcApi, dmuser = dm_setup(process)
    folder_prefix = gen_folder_prefix()

    for ii in range(num_rep):
        yield from bps.sleep(wait_time)

        if sample_move:
            yield from mesh_grid_move()

        file_name = f"{folder_prefix}_f{num_frames:06d}_r{ii+1:05d}"
        yield from setup_pilatus_int_series(acq_time, num_frames, file_name)

        print(f"\nStarting Measurement {file_name}")
        yield from pilatus_acquire()
        print(f"Measurement {file_name} Complete")

        metadata_fname = pv_registers.metadata_full_path.get()
        create_nexus_format_metadata(metadata_fname, det=pilatus1m)

        dm_run_job("eiger", process, workflowProcApi, dmuser, file_name)
    # except KeyboardInterrupt:
    #     raise RuntimeError("\n Bluesky plan stopped by user (Ctrl+C).")
    # except Exception as e:
    #     print(f"Error occurred during measurement: {e}")
    # finally:
    #     pass
