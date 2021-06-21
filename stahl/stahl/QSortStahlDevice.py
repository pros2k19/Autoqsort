import logging
from tango.server import Device, attribute, command
from tango import DevState

from .device import Stahl, QSortStahl

logger = logging.getLogger(__name__)


class QSortStahlDevice(Device):
    def init_device(self):
        try:
            stahl = Stahl()
            qsort_stahl = QSortStahl(stahl)
        except Exception as e:
            logger.exception("error initializing stahl device")
            raise
        self._dev = qsort_stahl
        logger.debug("before super().init_device()")
        super().init_device()
        self.set_state(DevState.ON)
        logger.debug("end of init_device")

    @command
    def set_zero(self):
        self._dev.set_zero()

    @command
    def disconnect(self):
        self._dev.close()
        self.set_state(DevState.OFF)

    @command
    def connect(self):
        self._dev.init()
        self.set_state(DevState.ON)

    @attribute(label='Heat', dtype=float)
    def heat(self):
        return self._dev.heat

    @heat.write
    def heat(self, heat):
        self._dev.set_heat(heat)

    @attribute(label='AStig', dtype=float)
    def astig(self):
        return self._dev.astig

    @astig.write
    def astig(self, astig):
        self._dev.set_astig(astig)

    @attribute(label='F/L-Ratio', dtype=float)
    def fl_ratio(self):
        return self._dev.fl_ratio

    @fl_ratio.write
    def fl_ratio(self, fl_ratio):
        self._dev.set_fl_ratio(fl_ratio)

    @attribute(label='S1', dtype=float)
    def s1(self):
        return self._dev.s1

    @s1.write
    def s1(self, s1):
        self._dev.set_s1(s1)

    @attribute(label='S2', dtype=float)
    def s2(self):
        return self._dev.s2

    @s2.write
    def s2(self, s2):
        self._dev.set_s2(s2)
