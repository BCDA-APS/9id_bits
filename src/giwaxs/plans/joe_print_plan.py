def joe_print_plan():
    """Demonstrate a ``print()`` plan stub (no data streams)."""
    """
    logger.debug("sim_print_plan()")
    """
    """
    yield from bps.null()
    sim_det = oregistry["sim_det"]
    sim_motor = oregistry["sim_motor"]
    """
    print("joe_print_plan(): This is a test.")
    """
    print(f"sim_print_plan():  {sim_motor.position=}  {sim_det.read()=}.")
    """

