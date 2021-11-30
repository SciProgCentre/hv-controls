import dataclasses
import math
from dataclasses import dataclass

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDoubleSpinBox, QHBoxLayout

from hv.hv_device import HVDevice
from hv.ui.generators import Generator, GeneratorWidget
from hv.ui.generators.widgets import add_voltage_current_controls


@dataclass
class StairsParameters:
    time_step: float
    voltage_step : float
    max_voltage : float
    current: float
    min_voltage: float = 0.0


class Stairs(Generator):
    NAME = "stairs"

    def __init__(self, device : HVDevice, parameters: dict = None):
        super(Stairs, self).__init__(device)
        if parameters is None:
            data = self.device.data
            self.parameters = StairsParameters(self.MIN_TICK, data.voltage_step, data.voltage_min, data.current_min)
        else:
            self.parameters = StairsParameters(**parameters)

    def start(self):
        self.current_voltage = self.parameters.min_voltage
        self.up = False
        self.setup(self.parameters.min_voltage, self.parameters.current)
        self.timer_id  = self.startTimer(self.parameters.time_step*1000, QtCore.Qt.PreciseTimer)

    def stop(self):
        self.killTimer(self.timer_id)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if self.device.is_open:
            if self.up:
                self.current_voltage += self.parameters.voltage_step
                if self.current_voltage > self.parameters.max_voltage:
                    self.up = False
                    self.setup(self.parameters.min_voltage, self.parameters.current)
                else:
                    self.setup(self.current_voltage, self.parameters.current)
            else:
                I, U = self.device.get_IU()
                if math.isclose(U, self.parameters.min_voltage, abs_tol=self.device.data.voltage_step):
                    self.up = True
                    self.current_voltage = self.parameters.min_voltage

        else:
            self.abort_signal.emit()


class StairsWidget(GeneratorWidget):
    def __init__(self, parent, generator: Stairs):
        super(StairsWidget, self).__init__(parent, generator)
        self.parameters = generator.parameters
        self.init_UI()

    def export_settings(self):
        return {self.generator.NAME :  dataclasses.asdict(self.parameters)}

    def _create_stairs_parameters(self, vbox):
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Time step, s: "))
        time_step_input = QDoubleSpinBox()
        time_step_input.setMinimum(self.generator.MIN_TICK)
        time_step_input.setSingleStep(self.generator.MIN_TICK)
        time_step_input.setMaximum(self.generator.MAX_PERIOD)
        time_step_input.setValue(self.parameters.time_step)
        hbox.addWidget(time_step_input)

        def time_step(value):
            self.parameters.time_step = value

        time_step_input.valueChanged.connect(time_step)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Voltage step, V: "))
        data = self.generator.device.data
        voltage_step_input = QDoubleSpinBox()
        voltage_step_input.setMinimum(data.voltage_step)
        voltage_step_input.setSingleStep(data.voltage_step)
        voltage_step_input.setMaximum(data.voltage_max)
        voltage_step_input.setValue(self.parameters.voltage_step)
        hbox.addWidget(voltage_step_input)

        def voltage_step(value):
            self.parameters.voltage_step = value

        voltage_step_input.valueChanged.connect(voltage_step)



    def init_UI(self):
        vbox = QVBoxLayout(self)
        add_voltage_current_controls(self, vbox, self.generator)
        self._create_stairs_parameters(vbox)