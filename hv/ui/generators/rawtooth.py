import math
from enum import Enum, auto

from PyQt5 import QtCore

from hv.ui.generators import ScanningGenerator


class RawtoothState(Enum):
    START = auto()
    RISE = auto()
    IMPULSE = auto()
    ZERO = auto()


class ReversedRawtoothWave(ScanningGenerator):
    NAME = "reversed rawtooth"

    def start(self):
        self.current_time = 0.0
        self.current_impulse_length = self.impulse_length()
        max_voltage = self.parameters.max_voltage
        min_voltage = self.parameters.min_voltage
        coeff = (max_voltage - min_voltage) / self.current_impulse_length
        self.voltage_step = self.MIN_TICK*coeff
        self.voltage = max_voltage
        self.state = RawtoothState.START
        self.timer_id  = self.startTimer(self.MIN_TICK*1000, QtCore.Qt.PreciseTimer)

    def stop(self):
        self.killTimer(self.timer_id)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if self.device.is_open:
            self.current_time += self.MIN_TICK
            if self.state == RawtoothState.START:
                self.setup(self.voltage, self.parameters.current)
                self.state = RawtoothState.RISE
            elif self.state == RawtoothState.ZERO:
                if self.current_time > self.parameters.period:
                    self.current_time = 0
                    self.voltage = self.parameters.max_voltage
                    self.state = RawtoothState.START
            else:
                if self.state == RawtoothState.RISE:
                    I, U = self.device.get_IU()
                    if U > self.voltage or math.isclose(U, self.voltage, abs_tol=self.voltage_accuracy):
                      self.state = RawtoothState.IMPULSE

                if self.state == RawtoothState.IMPULSE:
                    self.setup(self.voltage, self.parameters.current)
                    self.voltage -= self.voltage_step
                    if self.voltage < self.parameters.min_voltage:
                        self.voltage = self.parameters.min_voltage

                if self.current_time >= self.current_impulse_length:
                    self.state = RawtoothState.ZERO
                    if self.voltage > self.parameters.min_voltage:
                        self.voltage = self.parameters.min_voltage
                        self.device.set_value(self.voltage, self.parameters.current)
        else:
            self.abort_signal.emit()