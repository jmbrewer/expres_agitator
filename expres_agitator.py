"""
    EXPRES Fiber Agitator Interface Class

    This provides a class to send commands to and receive information from
    a dual-channel Roboclaw voltage controller controlling the two DC motors
    for fiber agitation.
"""
import numpy as np
from roboclaw import Roboclaw

__DEFAULT_PORT__ = 'COM4'
__DEFAULT_BAUD_RATE__ = 38400
__DEFAULT_ADDR__ = 0x80
__DEFAULT_TIMEOUT__ = 3.0
__DEFAULT_RETRIES__ = 3
__DEFAULT_INTER_BYTE_TIMEOUT__ = 1.0

class Agitator:

    port = __DEFAULT_PORT__
    baud_rate = __DEFAULT_BAUD_RATE__
    addr = __DEFAULT_ADDR__
    timeout = __DEFAULT_TIMEOUT__
    retries = __DEFAULT_RETRIES__
    inter_byte_timeout = __DEFAULT_INTER_BYTE_TIMEOUT__

    _rc = Roboclaw(comport=port,
                   rate=baud_rate,
                   addr=addr,
                   timeout=timeout,
                   retries=retries,
                   inter_byte_timeout=inter_byte_timeout)

    def __init__(self):
        pass

    @classmethod
    def start_agitation(cls, exp_time=2):
        cls.setVoltage1(Motor1.calc_voltage(exp_time))
        cls.setVoltage2(Motor2.calc_voltage(exp_time*0.9))

    @classmethod
    def stop_agitation(cls):
        cls.setVoltage(0)

    @classmethod
    def set_voltage(cls, voltage):
        cls.setVoltage1(voltage)
        cls.setVoltage2(voltage)

    @classmethod
    def set_voltage1(cls, voltage):
        battery_voltage = cls.battery_voltage
        if abs(voltage) > battery_voltage:
            voltage = np.sign(voltage) * battery_voltage
        if voltage >= 0:
            cls._rc.ForwardM1(int(voltage/battery_voltage*127))
        else:
            cls._rc.BackwardM1(int(-voltage/battery_voltage*127))
        cls.voltage1 = voltage

    @classmethod
    def set_voltage2(cls, voltage):
        battery_voltage = cls.battery_voltage
        if abs(voltage) > battery_voltage:
            voltage = np.sign(voltage) * battery_voltage
        if voltage >= 0:
            cls._rc.ForwardM2(int(voltage/battery_voltage*127))
        else:
            cls._rc.BackwardM2(int(-voltage/battery_voltage*127))
        cls.voltage2 = voltage

    @property
    @classmethod
    def battery_voltage(cls):
        return cls._rc.ReadMainBatteryVoltage()[1] / 10

    @classmethod
    def get_max_voltage(cls):
        return cls._rc.ReadMinMaxMainVoltages()[2] / 10

    @classmethod
    def set_max_voltage(cls, voltage):
        cls._rc.SetMainVoltages(int(self.min_voltage*10), int(voltage*10))

    max_voltage = property(get_max_voltage, set_max_voltage)

    @classmethod
    def get_min_voltage(cls):
        return cls._rc.ReadMinMaxMainVoltages()[1] / 10

    @classmethod
    def set_min_voltage(cls, voltage):
        cls._rc.SetMainVoltages(int(voltage*10), int(self.max_voltage*10))

    min_voltage = property(get_min_voltage, set_min_voltage)

    @property
    @classmethod
    def current1(cls):
        return cls._rc.ReadCurrents()[1]/100

    @property
    @classmethod
    def current2(cls):
        return cls._rc.ReadCurrents()[2]/100

    @property
    @classmethod
    def max_current1(cls):
        return cls._rc.ReadM1MaxCurrent()[1]/100

    @max_current1.setter
    @classmethod
    def max_current1(cls, current):
        cls._rc.SetM1MaxCurrent(current)

    @property
    @classmethod
    def max_current2(cls):
        return cls._rc.ReadM2MaxCurrent()[1]/100

    @max_current2.setter
    @classmethod
    def max_current2(cls, current):
        cls._rc.SetM2MaxCurrent(current)

class Motor:
    """
    Class that determines a voltage for a motor given the slope and intercept
    of the voltage vs. frequency regression
    """
    slope = 0.0
    intercept = 0.0
    min_voltage = 0.0
    
    @classmethod
    def calc_voltage(cls, exp_time=2.0):
        """
        Calculate the voltage for the motor given an exposure time in seconds
        """
        if exp_time <= 0:
            return cls.calc_voltage(2.0)
        voltage = cls.slope / exp_time + cls.intercept
        if voltage > Agitator.battery_voltage:
            return Agitator.battery_voltage
        elif voltage < cls.min_voltage:
            return cls.min_voltage
        return voltage

class Motor1(Motor):
    slope = 19.7
    intercept = 3.1
    min_voltage = 10.0

class Motor2(Motor):
    slope = 27.1
    intercept = 1.7
    min_voltage = 5.0
