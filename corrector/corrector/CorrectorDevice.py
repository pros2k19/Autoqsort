import os
import time
import logging

from PIL import Image
import numpy as np
from tango.server import Device, command, attribute, device_property
import rpyc

from qsort_infra.templatematch import find_match

from dac import serialize_dac

TEMPLATE_DIR = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


class RemoteCorrectorGUI:
    def __init__(self, host="192.168.0.2", dac_file=None):
        self._conn = rpyc.classic.connect(host)
        if dac_file is None:
            _os = self._conn.modules.os
            # Has to be backspace, so not local os.path.join
            self._dac_file = _os.path.join(_os.environ.get('TEMP', ''), 'tmp.dac')
        else:
            self._dac_file = dac_file

        self._corr_file = np.array(self._local_image('corr_file.png'))
        self._corr_file_active = np.array(self._local_image('corr_file_active.png'))
        self._merge_dialog = np.array(self._local_image('merge_dialog.png'))
        self.snapshot()
        self._last_load = time.time()
        self._cache = {}

    def _remote_image(self, template):
        with open(os.path.join(TEMPLATE_DIR, template), 'rb') as f:
            data = f.read()
            Image = self._conn.modules['PIL.Image']
            _io = self._conn.modules['io']
            return Image.open(_io.BytesIO(data))

    def _local_image(self, template):
        return Image.open(os.path.join(TEMPLATE_DIR, template))

    def snapshot(self):
        _pyautogui = self._conn.modules['pyautogui']
        screen = _pyautogui.screenshot()
        # FIXME speed up with fast correlation?
        print(self._corr_file.shape)
        print(self._corr_file_active.shape)
        print(screen)
        window_locations = find_match(self._corr_file, screen)
        window_locations_active = find_match(self._corr_file_active, screen)
        if window_locations and window_locations_active:
            raise RuntimeError("Both active and inactive corrector GUI titles found!")
        elif (not window_locations) and (not window_locations_active):
            raise RuntimeError("No corrector GUI title found!")
        if window_locations_active:
            window_locations = window_locations_active
        # x, y
        self._location = window_locations[0]

    def load_dac(self, dacfile):
        _pyautogui = self._conn.modules['pyautogui']
        delay = time.time() - self._last_load
        assert delay >= 0
        if delay < 1:
            time.sleep(1 - delay)
        x, y = self._location
        # activate window
        _pyautogui.click(x+60, y+5)
        time.sleep(0.1)
        # Hotkey for File -> merge
        _pyautogui.hotkey('ctrl', 'm')
        # wait for file opening dialogue
        # start = time.time()
        time.sleep(0.1)
        # Commented out: Wait and confirm that dialogue is opened
        # TODO re-implement with fast correlation
        # while _pyautogui.locateOnScreen(self._merge_dialog) is None:
        #     if time.time() - start > 10:
        #         raise RuntimeError("Open file dialogue not detected within timeout period")
        #     time.sleep(0.5)
        # Filename field is in focus
        _pyautogui.typewrite(dacfile)
        _pyautogui.press('enter')
        self._last_load = time.time()
        # Time required to merge: GUI is greyed out during that time
        # time.sleep(0.8)

    def set(self, key, value):
        dac_settings = {key: value}
        data = serialize_dac(dac_settings)
        with self._conn.builtins.open(self._dac_file, 'w') as f:
            f.write(data)
        self.load_dac(self._dac_file)
        self._cache[key] = value

    def get(self, key):
        return self._cache.get(key)


class CorrectorDevice(Device):
    rpyc_host = device_property(dtype=str, default_value="192.168.0.2")
    dac_file = device_property(dtype=str, default_value=None)

    def init_device(self):
        try:
            print("init...")
            Device.init_device(self)
            self._corrector_device = RemoteCorrectorGUI(self.rpyc_host, self.dac_file)
            print("init done.")
        except Exception:
            logging.exception("initialization failed")
            raise

    @command()
    def snapshot(self):
        self._corrector_device.snapshot()

    @attribute(label='ADL', dtype=float, unit='mA')
    def ADL(self) -> float:
        try:
            print("get ADL")
            res = self._corrector_device.get('ADL')
            # to avoid issues with "None"
            if res is None:
                res = 0
            print("ADL result", res)
        except Exception as e:
            print(e)
            res = -1
        return res

    @ADL.write
    def ADL(self, value):
        print("setting ADL")
        self._corrector_device.set('ADL', value)
        print("ADL set")


if __name__ == '__main__':
    g = RemoteCorrectorGUI()

