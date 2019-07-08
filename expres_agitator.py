"""
    EXPRES Fiber Agitator Interface Module

    Provides a class to send commands to and receive information from a
    dual-channel Roboclaw voltage controller controlling the two DC motors
    for fiber agitation. Can also be run as a script to simply control the
    fiber agitator from a terminal.
"""
import numpy as np
import time
from threading import Thread, Event
import logging, logging.handlers
from roboclaw import Roboclaw


__DEFAULT_PORT__ = 'COM12'
__DEFAULT_BAUD_RATE__ = 38400
__DEFAULT_ADDR__ = 0x80
__DEFAULT_TIMEOUT__ = 3.0
__DEFAULT_RETRIES__ = 3
__DEFAULT_INTER_BYTE_TIMEOUT__ = 1.0


class Agitator(object):
    """Class for controlling the EXPRES fiber agitator
    
    Inputs
    ------
    comport : str
        The hardware COM Port for the Roboclaw motor controller

    Public Methods
    --------------
    start(exp_time, timeout, rot1, rot2):
        Threaded agitation
    start_agitation(exp_time, rot1, rot2):
        Unthreaded agitation
    stop():
        Stop either threaded or unthreaded agitation
    stop_agitation():
        Hard-stop agitation but will not close thread
    """

    def __init__(self, comport=__DEFAULT_PORT__):
        self._rc = Roboclaw(comport=comport,
                rate=__DEFAULT_BAUD_RATE__,
                addr=__DEFAULT_ADDR__,
                timeout=__DEFAULT_TIMEOUT__,
                retries=__DEFAULT_RETRIES__,
                inter_byte_timeout=__DEFAULT_INTER_BYTE_TIMEOUT__)

        # Create a logger for the agitator
        self.logger = logging.getLogger('expres_agitator')
        self.logger.setLevel(logging.DEBUG)

        # Create file handler to log all messages
        try:
            fh = logging.handlers.TimedRotatingFileHandler(
                'C:/Users/admin/agitator_logs/agitator.log',
                when='D',
                interval=1,
                utc=True,
                backupCount=10)
        except FileNotFoundError:
            fh = logging.handlers.TimedRotatingFileHandler(
                'agitator.log',
                when='D',
                interval=1,
                utc=True,
                backupCount=10)
        fh.setLevel(logging.DEBUG)

        # Create console handler to log info messages
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.thread = None # In case stop() is called before a thread is created
        self.stop_event = Event() # Used for stopping threads
        self.stop_agitation() # Just to make sure

    def __del__(self):
        """
        When the object is deleted, make sure all threads are closed and
        agitator is stopped. Unfortunately, these actions cannot be logged
        because the logger closes by the time __del__ is called...
        """
        self.stop(verbose=False)
        self.stop_agitation(verbose=False)

    def threaded_agitation(self, exp_time, timeout, **kwargs):
        """Threadable function allowing stop event"""
        self.logger.info(f'Starting agitator thread for {exp_time}s exposure with {timeout}s timeout')
        self.start_agitation(exp_time, **kwargs)

        t = 0
        start_time = time.time()
        while not self.stop_event.is_set() and t < timeout:
            time.sleep(1)
            t = time.time() - start_time
            # self.logger.info(f'{round(t, 1)}/{timeout}s for {exp_time}s exposure. I1: {self.current1}, I2: {self.current2}')
            self.logger.info(f'{round(t, 1)}/{timeout}s for {exp_time}s exposure')

        self.stop_agitation()

    def start(self, exp_time=60.0, timeout=None, **kwargs):
        """
        Start a thread that starts agitation and stops if a stop event is
        called or if the timeout is reached
        """
        self.stop() # To close any previously opened threads

        if timeout is None: # Allow for some overlap time
            timeout = exp_time + 10.0

        self.thread = Thread(target=self.threaded_agitation,
                             args=(exp_time, timeout),
                             kwargs=kwargs)
        self.thread.start()

    def stop(self, verbose=True):
        """Stop the agitation thread if it is running"""
        if self.thread is not None and self.thread.is_alive():
            while self.voltage1 > 0 or self.voltage2 > 0:
                if verbose:
                    self.logger.info('Attempting to stop threaded agitation')
                self.stop_event.set()
                self.thread.join(2)
        if self.voltage1 > 0 or self.voltage2 > 0:
            # As a backup in case something went wrong
            if verbose:
                self.logger.error('Something went wrong when trying to stop threaded agitation. Forcing agitator to stop.')
            self.stop_agitation()

    def start_agitation(self, exp_time=60.0, rot=None):
        """Set the motor voltages for the given number of rotations in exp_time"""
        if exp_time < 0:
            self.logger.warning('Negative exposure time given to agitator object')
            self.stop_agitation()
            return
        elif exp_time == 0:
            self.logger.info('0.0s exposure time given to agitator object')
            self.stop_agitation()
            return

        if rot is None:
            rot = 0.5 * exp_time

        if rot < 0:
            self.logger.warning('Negative rotation number given to agitator object')
            self.stop_agitation()
            return
        elif rot == 0.0:
            self.logger.info('Zero rotation number given to agitator object')
            self.stop_agitation()
            return

        freq1 = rot/exp_time
        freq2 = 0.9*rot/exp_time
        self._freq = freq1

        self.logger.info(f'Starting agitation at approximately {self._freq} Hz')
        self.set_voltage1(Motor1.calc_voltage(self.battery_voltage, freq1))
        self.set_voltage2(Motor2.calc_voltage(self.battery_voltage, freq2))

    def stop_agitation(self, verbose=True):
        """Set both motor voltages to 0"""
        if verbose:
            self.logger.info('Stopping agitation')
        self.set_voltage(0)
        self._freq = 0
        self.stop_event.clear() # Allow for future agitation events

    def set_voltage(self, voltage):
        """Set both motor voltages to the given voltage"""
        self.set_voltage1(voltage)
        self.set_voltage2(voltage)

    # Getter for the frequency

    def get_freq(self):
        self.logger.info('Requesting frequency')
        return self._freq

    # Getters and setters for the motor voltages

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

    # Getter for the motor controller power source voltage

    def get_battery_voltage(self):
        voltage = self._rc.ReadMainBatteryVoltage()[1] / 10
        # Check to make sure the voltage is correct
        if not voltage > 0.0:
            voltage = 24.0
        return voltage

    battery_voltage = property(get_battery_voltage)

    # Getters and setters for the motor currents

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
    # Approximately the average parameters of Motor 1 and Motor 2
    slope = 28.0
    intercept = 1.8
    max_freq = 0.5
    min_voltage = 5.0
    
    @classmethod
    def calc_voltage(cls, battery_voltage, freq=0.5):
        """Calculate the voltage for the motor given a number of rotations per second"""
        if freq > cls.max_freq:
            freq = cls.max_freq

        voltage = cls.slope * freq + cls.intercept

        if voltage > battery_voltage:
            return battery_voltage
        elif voltage < cls.min_voltage:
            return cls.min_voltage
        return voltage

class Motor1(Motor):
    """Subclass of Motor with the parameters of Motor 1"""
    slope = 27.81
    intercept = 2.06
    max_freq = 0.5

class Motor2(Motor):
    """Subclass of Motor with the parameters of Motor 2"""
    slope = 28.49
    intercept = 1.58
    max_freq = 0.45

if __name__ == '__main__':
    """Script to allow terminal control of the motors
    
    To run, execute from the containing folder:
    python expres_agitator.py <com_port>
    where <com_port> is the name of the COM Port (typically COM13 on expres2)

    Terminal will then show
    Exposure time (s):

    Input the appropriate exposure time and press enter. If you would like to
    stop the agitator input 0. If you would like to close the program, input
    anything that is not a number (or press ctrl-c).
    """
    import sys

    com_port = sys.argv[1]

    ag = Agitator(com_port)

    while True:
        try:
            freq = float(input('Frequency (Hz): '))
        except ValueError: # catch when exp_time is not a number
            print('Number was not input. Exiting...')
            break

        ag.start_agitation(exp_time=60.0, rot=60.0*freq)
        time.sleep(1)

    ag.stop_agitation()