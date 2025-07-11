"""
db_2slit_soft: synApps optics 2slit_soft.db


db_2list_soft.vdb uses soft motors for the xn, xp, size and center.

Duplicates db_2slit using the HV configuration:

Coordinates of ``Optics2Slit2D_HV`` (viewing from detector towards source)::

        v.xp
    h.xn    h.xp
        v.xn

Each blade [#]_ travels in a _cartesian_ coordinate
system.  Positive motion moves a blade **outwards** (towards the ``p`` suffix).
Negative motion moves towards the ``n`` suffix.  Size and center are computed
by the underlying EPICS support.

    hsize = out - inb
    vsize = top - bot

..  [#] Note that the blade names here may be different than the EPICS support.
    The difference is to make the names of the blades consistent with other
    slits with the Bluesky framework.

USAGE::

    slit1 = Optics2Slit2D_soft("gp:Slit1", name="slit1")
    slit1.geometry = 0.1, 0.1, 0, 0  # moves the slits
    print(slit1.geometry)

    slit2 = Optics2Slit_InbOutBotTop("gp:Slit2", name="slit2")
    slit2.geometry = 0.1, 0.1, 0, 0  # moves the slits
    print(slit2.geometry)

Public Structures

.. autosummary::

    ~c_soft
    ~Optics2Slit2D_soft

:see: https://github.com/epics-modules/optics

new in release 1.6.0
"""
import logging

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsMotor

from apstools.utils import SlitGeometry

logger = logging.getLogger(__name__)
logger.info(__file__)


class Optics2Slit1D_soft(Device):
    """
    EPICS synApps optics 2slit.db 1D support: xn, xp, size, center, sync

    "sync" is used to tell the EPICS 2slit database to synchronize the
    virtual slit values with the actual motor positions.
    """

    xn = Cpt(EpicsMotor, "xn")
    xp = Cpt(EpicsMotor, "xp")
    size = Cpt(EpicsMotor, "size")
    center = Cpt(EpicsMotor, "center")

    sync = Cpt(EpicsSignal, "doSync", put_complete=True, kind="omitted")


class Optics2Slit2D_soft(Device):
    """
    EPICS synApps optics 2slit_soft.vdb 2D support: h.xn, h.xp, v.xn, v.xp
    """

    h = Cpt(Optics2Slit1D_soft, "H")
    v = Cpt(Optics2Slit1D_soft, "V")

    @property
    def geometry(self):
        """Return the slit 2D size and center as a namedtuple."""
        pppp = [
            round(obj.position, obj.precision) for obj in (self.h.size, self.v.size, self.h.center, self.v.center)
        ]

        return SlitGeometry(*pppp)

    @geometry.setter
    def geometry(self, value):
        # first, test the input by assigning it to local vars
        width, height, x, y = value

        self.h.size.move(width)
        self.v.size.move(height)
        self.h.center.move(x)
        self.v.center.move(y)
