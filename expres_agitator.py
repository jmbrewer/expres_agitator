"""
    EXPRES Fiber Agitator Interface Class

    This provides a class to send commands to and receive information from
    a dual-channel Roboclaw voltage controller controlling the two DC motors
    for fiber agitation.
"""
import numpy as np
from roboclaw import Roboclaw

__DEFAULT_PORT__ = 'COM13'
__DEFAULT_BAUD_RATE__ = 38400
__DEFAULT_ADDR__ = 0x80
__DEFAULT_TIMEOUT__ = 3.0
__DEFAULT_RETRIES__ = 3
__DEFAULT_INTER_BYTE_TIMEOUT__ = 1.0

class Agitator:

    def __init__(self, comport=__DEFAULT_PORT__):
        self._rc = Roboclaw(comport=comport,
                rate=__DEFAULT_BAUD_RATE__,
                addr=__DEFAULT_ADDR__,
                timeout=__DEFAULT_TIMEOUT__,
                retries=__DEFAULT_RETRIES__,
                inter_byte_timeout=__DEFAULT_INTER_BYTE_TIMEOUT__)
        # self.stop_agitation()

    def start_agitation(self, exp_time=2.0, rot1=10.0, rot2=9.0):
        self.set_voltage1(Motor1.calc_voltage(self.battery_voltage, exp_time, rot1))
        self.set_voltage2(Motor2.calc_voltage(self.battery_voltage, exp_time, rot2))

    def stop_agitation(self):
        self.set_voltage(0)

    def stop(self):
        self.stop_agitation()

    def set_voltage(self, voltage):
        self.set_voltage1(voltage)
        self.set_voltage2(voltage)

    def get_voltage1(self):
        return self._voltage1

    def set_voltage1(self, voltage):
        battery_voltage = self.battery_voltage
        if abs(voltage) > battery_voltage:
            voltage = np.sign(voltage) * battery_voltage
        if voltage >= 0:
            self._rc.ForwardM1(int(voltage/battery_voltage*127))
        else:
            self._rc.BackwardM1(int(-voltage/battery_voltage*127))
        self._voltage1 = voltage

    voltage1 = property(get_voltage1, set_voltage1)

    def get_voltage2(self):
        return self._voltage2

    def set_voltage2(self, voltage):
        battery_voltage = self.battery_voltage
        if abs(voltage) > battery_voltage:
            voltage = np.sign(voltage) * battery_voltage
        if voltage >= 0:
            self._rc.ForwardM2(int(voltage/battery_voltage*127))
        else:
            self._rc.BackwardM2(int(-voltage/battery_voltage*127))
        self._voltage2 = voltage

    voltage2 = property(get_voltage2, set_voltage2)

    def get_battery_voltage(self):
        return self._rc.ReadMainBatteryVoltage()[1] / 10

    battery_voltage = property(get_battery_voltage)

    def get_max_voltage(self):
        return self._rc.ReadMinMaxMainVoltages()[2] / 10

    def set_max_voltage(self, voltage):
        self._rc.SetMainVoltages(int(self.min_voltage*10), int(voltage*10))

    max_voltage = property(get_max_voltage, set_max_voltage)

    def get_min_voltage(self):
        return self._rc.ReadMinMaxMainVoltages()[1] / 10

    def set_min_voltage(self, voltage):
        self._rc.SetMainVoltages(int(voltage*10), int(self.max_voltage*10))

    min_voltage = property(get_min_voltage, set_min_voltage)

    def get_current1(self):
        return self._rc.ReadCurrents()[1]/100

    current1 = property(get_current1)

    def get_current2(self):
        return self._rc.ReadCurrents()[2]/100

    current2 = property(get_current2)

    def get_max_current1(self):
        return self._rc.ReadM1MaxCurrent()[1]/100

    def set_max_current1(self, current):
        self._rc.SetM1MaxCurrent(current)

    max_current1 = property(get_max_current1, set_max_current1)

    def get_max_current2(self):
        return self._rc.ReadM2MaxCurrent()[1]/100

    def set_max_current2(self, current):
        self._rc.SetM2MaxCurrent(current)

    max_current2 = property(get_max_current2, set_max_current2)

class Motor:
    """
    Class that determines a voltage for a motor given the slope and intercept
    of the voltage vs. frequency regression
    """
    slope = 28.0
    intercept = 1.8
    min_voltage = 5.0
    
    @classmethod
    def calc_voltage(cls, battery_voltage, exp_time=2.0, n_rotations=10.0):
        """
        Calculate the voltage for the motor given an exposure time in seconds
        """
        if exp_time <= 0:
            exp_time = 2.0
        voltage = cls.slope / (exp_time/n_rotations) + cls.intercept
        if voltage > battery_voltage:
            return battery_voltage
        elif voltage < cls.min_voltage:
            return cls.min_voltage
        return voltage

class Motor1(Motor):
    slope = 27.81
    intercept = 2.06

class Motor2(Motor):
    slope = 28.49
    intercept = 1.58
