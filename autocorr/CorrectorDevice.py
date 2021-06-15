import os

import tango
from tango.server import Device, command, attribute, device_property
import rpyc

from client import ControlSocketClient
from encoding import decode_lens_current, encode_lens_current
from mode import HF5000IllumMode, HF5000ImagingMode

TEMPLATE_DIR = os.path.dirname(__file__)


class RemoteCorrectorGUI:
    def __init__(self, dac_folder=None):
        self._conn = rpyc.classic.connect("192.168.0.2")
        self._pyautogui = self._conn.modules['pyautogui']
        if dac_folder is None:
            remote_os = self._conn.modules['os']
            self._dac_folder = remote_os.environ.get('PATH', '')
        else:
            self._dac_folder = dac_folder

        _PIL = self._conn.modules['PIL']
        _io = self._conn.modules['io']
        with open(os.path.join(TEMPLATE_DIR, 'corr_file.png')) as f:
            data = f.read()
            self._corr_file = _PIL.Image.open(_io.BytesIO(data))



class HF5000Device(Device):
    dac_folder = device_property(dtype=str, default_value=None)

    def init_device(self):
        

    @command
    def snapshot(self):
        self._pyautogui.
        pass

    @command
    async def connect_to_microscope(self):
        self._dev = ControlSocketClient('192.168.10.1')
        await self._dev.connect()

    @command
    async def disconnect(self):
        self._dev.close()

    async def _get_modes(self):
        modes = await self._dev.get("Column", "Mode")
        mode, submode = modes.value.split(",")
        mode = HF5000IllumMode.get_by_proto_value(int(mode, 16))
        submode = HF5000ImagingMode.get_by_proto_value(int(submode, 16))
        return mode, submode

    @attribute(label='Illumination mode', dtype=HF5000IllumMode)
    async def mode(self) -> HF5000IllumMode:
        modes = await self._get_modes()
        return modes[0]

    @mode.write
    async def mode(self, new_mode: HF5000IllumMode):
        # FF means keep submode (imaging mode) the same
        modes = "%s,FF" % new_mode.serialize()
        await self._dev.set("Column", "Mode", modes)

    @attribute(label='Imaging mode', dtype=HF5000ImagingMode)
    async def submode(self) -> HF5000ImagingMode:
        modes = await self._get_modes()
        return modes[1]

    @submode.write
    async def submode(self, new_mode: HF5000ImagingMode):
        # FF means keep mode (illumination mode) the same
        modes = "FF,%s" % new_mode.serialize()
        await self._dev.set("Column", "Mode", modes)

    @attribute(label='OBJ Lens', unit='A', dtype=float)
    async def obj_lens(self):
        await self._get_lens_current("OBJ")

    @obj_lens.write
    async def obj_lens(self, new_current: float):
        await self._set_lens_current("OBJ", new_current)

    @attribute(label='C1 Lens', unit='A', dtype=float)
    async def c1_lens(self):
        await self._get_lens_current("C1")

    @c1_lens.write
    async def c1_lens(self, new_current: float):
        await self._set_lens_current("C1", new_current)

    @attribute(label='C2 Lens', unit='A', dtype=float)
    async def c2_lens(self):
        await self._get_lens_current("C2")

    @c2_lens.write
    async def c2_lens(self, new_current: float):
        await self._set_lens_current("C2", new_current)

    @attribute(label='C3 Lens', unit='A', dtype=float)
    async def c3_lens(self):
        await self._get_lens_current("C3")

    @c3_lens.write
    async def c3_lens(self, new_current: float):
        await self._set_lens_current("C3", new_current)

    async def _get_highvoltage(self):
        return float((await self._dev.get("HighVoltage", "Value")).value)

    async def _get_lens_current(self, lens_name: str):
        # TODO: replace Get call with inform?
        voltage = await self._get_highvoltage()
        lens_value_raw = await self._dev.get("Lens", lens_name)
        return decode_lens_current(
            lens_value_raw.value,
            voltage,
            lens_name.upper(),
        )

    async def _set_lens_current(self, lens_name: str, current: float):
        # TODO: replace Get call with inform?
        voltage = await self._get_highvoltage()
        encoded = encode_lens_current(current, voltage, lens_name)
        await self._dev.set("Lens", lens_name, encoded)

    @attribute(label='Emission current', unit='µA')
    async def emission_current(self):
        resp = await self._dev.get('EmissionCurrent', 'Value')
        return float(resp.value)

    @attribute(label='Acceleration Voltage', unit='kV')
    async def acc_voltage(self):
        return await self._get_highvoltage()

    @command
    async def start_scanning(self):
        resp = await self._dev.set('ScanningImage', 'Run')
        return resp.code

    @command
    async def stop_scanning(self):
        resp = await self._dev.set('ScanningImage', 'Stop')
        return resp.code

    @command
    async def do_capture(self):
        resp = await self._dev.set('ScanningImage', 'Capture', r'')

    # - Stage (x/y/z)
    # scripts for focus series


if __name__ == "__main__":
    HF5000Device.run_server()
