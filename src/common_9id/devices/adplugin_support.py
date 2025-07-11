"""
EPICS area_detector helpers
"""

__all__ = """
    prepare_ROI
    prepare_STATS
""".split()

import bluesky.plan_stubs as bps

def prepare_ROI(detector, ROI_num = 1):
    name = 'roi'+str(ROI_num)
    try: 
        comp = getattr(detector, name)
    except:
        print(f"Can\'t find {name} in detector. Prep incomplete")
        return   
        
    # Enable
    comp.enable.set('Enable')
    
    print(f"{name} prepped")
        
def prepare_STATS(detector, 
    STATS_num = 1, 
    BEC = None,
    read_attrs = ["max_value", "min_value"]
    ):
    
    name = 'stats'+str(STATS_num)
    try: 
        comp = getattr(detector, name)
    except:
        print(f"Can\'t find {name} in detector. Prep incomplete")
        return
    
    # Set all hinted to normal unless in BEC list
    
    # Add in requested components to BEC
    if BEC is not None:
        for val_to_monitor in BEC:
            try:
                val = getattr(comp, val_to_monitor)
            except:
                print(f"Can\'t find {val_to_monitor} in {name} -- continuing")
            else:
                val.kind = 'hinted'

    # Clean up read attributes of detector
    if name not in detector.read_attrs:
        detector.read_attrs += [name]

    # Clean up read attributes of stats plugin
    for attr in read_attrs:
        if attr not in comp.read_attrs:
            comp.read_attrs += [attr]

    # Enable
    comp.enable.set('Enable')
    print(f"{name} prepped")
