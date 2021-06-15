import time
import logging

import pyvisa


logger = logging.getLogger(__name__)

"""
installation:
    pyvisa
    pyvisa-py
    pyserial (because the device is actually ttyUSB0...)
"""


class Stahl:
    """A simple example class"""

    def __init__(self):
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        assert len(resources) > 0
        self.inst = rm.open_resource(
            resources[0], read_termination="\r", write_termination="\r"
        )
        self.inst.baud_rate = 115200
        self.inst.write("IDN")
        time.sleep(0.010)
        s = self.inst.read()
        self.IDN = s[0:5]

    def set_voltage(self, a, ch):
        "this function allows to set a voltage of value -a- on a specific channel"
        if abs(a) <= 14:
            a = (a / 28) + 0.5
            command = "HV228 CH{:0{width}} {:.6f}".format(ch, a, width=2)
            self.inst.write(command)
            time.sleep(0.010)
            self.inst.read()

        else:
            a = 0.5
            logger.error("value exceeds the limits")
            command = "HV228 CH{:0{width}} {:.6f}".format(ch, a, width=2)
            self.inst.write(command)
            time.sleep(0.010)
            self.inst.read()

        return command

    def query_current(self, ch):
        current = "HV228 I{:0{width}}".format(ch, width=2)
        self.inst.write(current)
        time.sleep(0.010)
        c = self.inst.read()
        return current, c

    def query_voltage(self, ch):
        volt = "HV228 U{:0{width}}".format(ch, width=2)
        self.inst.write(volt)
        time.sleep(0.010)
        v = self.inst.read()
        return float(v.split()[0].replace(",", "."))

    def query_volt_curr(self, ch):
        V_C = "HV228 Q{:0{width}}".format(ch, width=2)
        self.inst.write(V_C)
        time.sleep(0.08)
        val = self.inst.read()
        return V_C, val

    def close_instrument(self):
        "puts to zero all the channels and closes the instrument"
        a = 0
        for i in range(1, 17):
            ch = i
            cmd = self.set_voltage(a, ch)
            self.inst.write(cmd)
            time.sleep(0.010)
            self.inst.read()
        logger.info("instrument closed")
        self.inst.close()


class QSortStahl:
    S1_pins = [1, 7, 2, 6, 5, 8, 3, 0]
    S2_pins = [12, 4, 9, 0, 10, 11, 13, 0]

    def __init__(self, stahl_device):
        self.device = stahl_device
        self.heat = 0
        self.astig = 0
        self.fl_ratio = 0
        self.s1 = 0
        self.s2 = 0

    def set_heat(self, heat):
        self.heat = heat

    def set_astig(self, astig):
        self.astig = astig

    def set_fl_ratio(self, fl_ratio):
        self.fl_ratio = fl_ratio

    def set_s1(self, s1):
        self.s1 = s1
        S1_volts = [0, 0, 0, 0, 0, 0, 0, 0]
        S1_volts[0] = s1 + self.heat
        S1_volts[1] = s1 - self.heat
        S1_volts[2] = -s1 * (0.5 + self.astig)
        S1_volts[3] = -s1 * (0.5 + self.astig)
        S1_volts[4] = s1 / 2
        S1_volts[5] = s1 / 2
        S1_volts[6] = -s1
        for i in range(8):
            self.device.set_voltage(S1_volts[i], self.S1_pins[i])
            logger.debug("setting voltage %f on pin %d", S1_volts[i], self.S1_pins[i])

    def set_s2(self, s2):
        self.s2 = s2
        S2_volts = [0, 0, 0, 0, 0, 0, 0, 0]
        S2_volts[0] = -s2 * self.fl_ratio
        S2_volts[1] = -s2
        S2_volts[2] = -s2
        S2_volts[3] = -s2
        S2_volts[4] = -s2
        S2_volts[5] = -s2 * self.fl_ratio
        S2_volts[6] = s2
        for i in range(8):
            self.device.set_voltage(S2_volts[i], self.S2_pins[i])
            logger.debug("setting voltage %f on pin %d", S2_volts[i], self.S2_pins[i])


if __name__ == "__main__":
    stahl = Stahl()
    device = QSortStahl(stahl)
    device.set_heat(0.8)
    device.set_astig(0)
    device.set_fl_ratio(0.62)
    device.set_s1(6.9)
    device.set_s2(8)
