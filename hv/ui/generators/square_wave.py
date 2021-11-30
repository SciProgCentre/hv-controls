from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from hv.hv_device import HVDevice
from hv.ui.generators import ScanningGenerator


class SquareWave(ScanningGenerator):
    NAME = "square wave"

    def start(self):
        self.length = int(self.impulse_length()*1000)
        period = int(self.parameters.period*1000)
        self.turn_on = True
        self.timer_period = self.startTimer(period,  QtCore.Qt.PreciseTimer)

    def stop(self):
        self.killTimer(self.timer_period)
        self.turn_on = False

    def down(self):
        if self.turn_on:
            self.setup(self.parameters.min_voltage, self.parameters.current)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if a0.timerId() == self.timer_period:
            if self.device.is_open:
                self.setup(self.parameters.max_voltage, self.parameters.current)
                QTimer.singleShot(self.length, self.down)
            else:
                self.abort_signal.emit()