import logging

import rpyc
from tango.server import Device, attribute
from tango import DevState

logger = logging.getLogger(__name__)


class QSortTEMDevice(Device):
    def init_device(self):
        super().init_device()
        try:
            conn = rpyc.classic.connect("192.168.0.2")
            ct = conn.modules['comtypes']
            ctc = conn.modules['comtypes.client']
            ct.CoInitialize()
            self.microscope = ctc.CreateObject('TEMScripting.Instrument.1')
        except Exception as e:
            logger.exception("failed to initialize")
            raise
 
    @attribute(label='User Shift X', dtype=float)
    def user_shift_x(self):
        return float(self.microscope.Illumination.Shift.X)

    @user_shift_x.write
    def user_shift_x(self, value):
        shift = self.microscope.Illumination.Shift
        shift.X = value
        self.microscope.Illumination.Shift = shift

    @attribute(label='User Shift Y', dtype=float)
    def user_shift_y(self):
        return float(self.microscope.Illumination.Shift.Y)
    
    @user_shift_y.write
    def user_shift_y(self, value):
        shift = self.microscope.Illumination.Shift
        shift.Y = value
        self.microscope.Illumination.Shift = shift

    @attribute(label='Intensity', dtype=float)
    def intensity(self):
        return float(self.microscope.Illumination.Intensity)

    @intensity.write
    def intensity(self, value):
        self.microscope.Illumination.Intensity = value