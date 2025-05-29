"""
registers: Bluesky support for NumRegsiters and StrRegisters at 9id

# Deprecated --> moved into devices.yml

"""

from bluesky import plan_stubs as bps
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class EpicsPvStorageRegisters(Device):

    file_name = Component(EpicsSignal, "StrReg1", string=True)
    file_path = Component(EpicsSignal, "StrReg2", string=True)
    metadata_full_path = Component(EpicsSignal, "StrReg3", string=True)
    qmap_file = Component(EpicsSignal, "StrReg4", string=True)
    analysis_machine = Component(EpicsSignal, "StrReg5", string=True)
    workflow_name = Component(EpicsSignal, "StrReg6", string=True)
    experiment_name = Component(EpicsSignal, "StrReg7", string=True)
    cycle_name = Component(EpicsSignal, "StrReg8", string=True)
    sample_name = Component(EpicsSignal, "StrReg9", string=True)
    spec_file = Component(EpicsSignal, "StrReg10", string=True)
    analysis_type = Component(EpicsSignal, "StrReg11", string=True)
    start_bluesky = Component(EpicsSignal, "StrReg12", string=True)
    det_name = Component(EpicsSignal, "StrReg13", string=True)

    measurement_num = Component(EpicsSignal, "Reg1")
    qnw_index = Component(EpicsSignal, "Reg2")

    sample0_pos = Component(EpicsSignal, "Reg3")
    sample1_pos = Component(EpicsSignal, "Reg4")
    sample2_pos = Component(EpicsSignal, "Reg5")
    sample3_pos = Component(EpicsSignal, "Reg6")
    sample4_pos = Component(EpicsSignal, "Reg7")
    sample5_pos = Component(EpicsSignal, "Reg8")
    sample6_pos = Component(EpicsSignal, "Reg9")
    sample7_pos = Component(EpicsSignal, "Reg10")
    sample8_pos = Component(EpicsSignal, "Reg11")
    sample9_pos = Component(EpicsSignal, "Reg12")
    sample10_pos = Component(EpicsSignal, "Reg13")
    sample11_pos = Component(EpicsSignal, "Reg14")
    sample12_pos = Component(EpicsSignal, "Reg15")
    sample13_pos = Component(EpicsSignal, "Reg16")
    sample14_pos = Component(EpicsSignal, "Reg17")
    sample15_pos = Component(EpicsSignal, "Reg18")
    sample16_pos = Component(EpicsSignal, "Reg19")
    sample17_pos = Component(EpicsSignal, "Reg20")
    sample18_pos = Component(EpicsSignal, "Reg21")
    sample19_pos = Component(EpicsSignal, "Reg22")
    sample20_pos = Component(EpicsSignal, "Reg23")
    sample21_pos = Component(EpicsSignal, "Reg24")
    sample22_pos = Component(EpicsSignal, "Reg25")
    sample23_pos = Component(EpicsSignal, "Reg26")
    sample24_pos = Component(EpicsSignal, "Reg27")
    sample25_pos = Component(EpicsSignal, "Reg28")
    sample26_pos = Component(EpicsSignal, "Reg29")
    sample27_pos = Component(EpicsSignal, "Reg30")

    eiger_det_x0 = Component(EpicsSignal, "Reg31")
    eiger_det_y0 = Component(EpicsSignal, "Reg32")
    eiger_db_x0 = Component(EpicsSignal, "Reg33")
    eiger_db_y0 = Component(EpicsSignal, "Reg34")
    rigaku_det_x0 = Component(EpicsSignal, "Reg35")
    rigaku_det_y0 = Component(EpicsSignal, "Reg36")
    rigaku_db_x0 = Component(EpicsSignal, "Reg37")
    rigaku_db_y0 = Component(EpicsSignal, "Reg38")
    current_det_x0 = Component(EpicsSignal, "Reg39")
    current_det_y0 = Component(EpicsSignal, "Reg40")
    current_db_x0 = Component(EpicsSignal, "Reg41")
    current_db_y0 = Component(EpicsSignal, "Reg42")

    def sample_position_register(self, qnw_index):
        """
        Return the indexed sample position register signal.

        """
        # if qnw_index <= 9:
        #     return getattr(self, f"sample{qnw_index}_pos")
        # else:
        #     return getattr(self, f"sample9_pos")
        
        return getattr(self, f"sample{qnw_index}_pos")


