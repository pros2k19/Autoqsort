import os
import time

from tango.server import Device, command, attribute, device_property
import rpyc
from PIL import Image
import numpy as np

from qsort_infra.templatematch import find_match


TEMPLATE_DIR = os.path.dirname(__file__)


class TEMSpyGUI:
    def __init__(self, host="192.168.0.2"):
        self._conn = rpyc.classic.connect(host)
        self._templates = {
            'PresetXL': (
                np.array(self._local_image('XL_active.png')),
                np.array(self._local_image('XL_inactive.png'))
            ),
            'Align_XS': (
                np.array(self._local_image('Align_XS_active.png')),
                np.array(self._local_image('Align_XS_inactive.png'))
            )
        }
        self.snapshot()
        self._cache = {}

    def keys(self):
        return self._templates.keys()

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
        screen_remote = _pyautogui.screenshot()
        screen_bytes = screen_remote.tobytes()
        screen_image = Image.frombytes(screen_remote.mode, screen_remote.size, screen_bytes)
        screen = np.array(screen_image)
        self._locations = {}
        for key in self.keys():
            active, inactive = self._templates[key]
            # FIXME speed up with fast correlation?
            window_locations = find_match(inactive, screen)
            window_locations_active = find_match(active, screen)
            if window_locations and window_locations_active:
                raise RuntimeError("Both active and inactive TEMSpy %s titles found!" % key)
            elif (not window_locations) and (not window_locations_active):
                self._locations[key] = None
                continue
            if window_locations_active:
                window_locations = window_locations_active
            # y, x -> x, y
            print(key)
            self._locations[key] = window_locations[0][1], window_locations[0][0]
    
    @property
    def PresetXL(self):
        return self._cache.get('PresetXL')

    @PresetXL.setter
    def PresetXL(self, val):
        loc = self._locations['PresetXL']
        if loc is None:
            raise RuntimeError("No PresetXL GUI title found!")
        x, y = loc
        _pyautogui = self._conn.modules['pyautogui']
        # Click on window title to activate window
        _pyautogui.click(x+60, y+5)
        _pyautogui.doubleClick(x+200, y+125)
        _pyautogui.press('backspace')
        _pyautogui.typewrite(str(val))
        _pyautogui.press('enter')
        self._cache['PresetXL'] = val

    @property
    def Align_XS(self):
        return self._cache.get('Align_XS', (None, None))

    @Align_XS.setter
    def Align_XS(self, vals):
        loc = self._locations['Align_XS']
        if loc is None:
            raise RuntimeError("No Align_XS GUI title found!")
        x, y = loc
        val1, val2 = vals
        _pyautogui = self._conn.modules['pyautogui']
        # Click on window title to activate window
        _pyautogui.click(x+60, y+5)
        
        _pyautogui.doubleClick(x+200, y+130)
        _pyautogui.press('backspace')
        _pyautogui.typewrite(str(val1))
        _pyautogui.doubleClick(x+200, y+150)
        _pyautogui.press('backspace')
        _pyautogui.typewrite(str(val2))
        _pyautogui.press('enter')
        self._cache['Align_XS'] = vals



class TEMSpyDevice(Device):
    rpyc_host = device_property(dtype=str, default_value="192.168.0.2")


    def init_device(self):
        print("init...")
        Device.init_device(self)
        self._spy_device = TEMSpyGUI(self.rpyc_host)
        print("init done.")

    @command()
    def snapshot(self):
        self._spy_device.snapshot()

    @attribute(label='PresetXL', dtype=float, unit='au')
    def PresetXL(self) -> float:
        try:
            print("get PresetXL")
            res = self._spy_device.PresetXL
            # to avoid issues with "None"
            if res is None:
                res = 0
            print("PresetXL result", res)
        except Exception as e:
            print(e)
            res = -1
        return res

    @PresetXL.write
    def PresetXL(self, value):
        print("setting PresetXL")
        self._spy_device.PresetXL = value
        print("PresetXL set")

    @attribute(label='Align_XS_1', dtype=float, unit='au')
    def Align_XS_1(self) -> float:
        try:
            print("get Align_XS_1")
            res = self._spy_device.Align_XS[0]
            # to avoid issues with "None"
            if res is None:
                res = 0
            print("Align_XS_1 result", res)
        except Exception as e:
            print(e)
            res = -1
        return res

    @Align_XS_1.write
    def Align_XS_1(self, value):
        print("setting Align_XS_1")
        prev = self._spy_device.Align_XS
        self._spy_device.Align_XS = (value, prev[1])
        print("Align_XS_1 set")

    @attribute(label='Align_XS_2', dtype=float, unit='au')
    def Align_XS_2(self) -> float:
        try:
            print("get Align_XS_2")
            res = self._spy_device.Align_XS[1]
            # to avoid issues with "None"
            if res is None:
                res = 0
            print("Align_XS_2 result", res)
        except Exception as e:
            print(e)
            res = -1
        return res

    @Align_XS_2.write
    def Align_XS_2(self, value):
        print("setting Align_XS_2")
        prev = self._spy_device.Align_XS
        self._spy_device.Align_XS = (prev[0], value)
        print("Align_XS_2 set")
