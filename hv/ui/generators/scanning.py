import dataclasses
from dataclasses import dataclass

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QDoubleSpinBox, QVBoxLayout

from hv.hv_device import HVDevice
from hv.ui.generators.base import Generator, GeneratorWidget
from hv.ui.generators.widgets import add_voltage_current_controls
from hv.ui.regulator import HVRegulator

@dataclass
class ScanningParameters:
    period : float
    max_voltage : float
    current: float
    min_voltage: float = 0.0
    duty_cycle: float = 0.5




class ScanningGenerator(Generator):

    def __init__(self, device : HVDevice, parameters: dict = None):
        super(ScanningGenerator, self).__init__(device)
        if parameters is None:
            self.parameters = ScanningParameters(self.MIN_PERIOD, device.data.voltage_min, device.data.current_min)
        else:
            self.parameters = ScanningParameters(**parameters)

    def duty_cycle_step(self):
        return self.MIN_TICK / self.parameters.period

    def impulse_length(self):
        return self.parameters.period * self.parameters.duty_cycle


class ScanningWidget(GeneratorWidget):
    def __init__(self, parent, generator: ScanningGenerator):
        super(ScanningWidget, self).__init__(parent, generator)
        self.parameters = generator.parameters
        self.init_UI()

    def export_settings(self):
        return {self.generator.NAME :  dataclasses.asdict(self.parameters)}

    def _create_time_parameters(self, vbox):
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Period, s: "))
        period_input = QDoubleSpinBox()
        period_input.setMinimum(self.generator.MIN_PERIOD)
        period_input.setSingleStep(self.generator.MIN_TICK)
        period_input.setMaximum(self.generator.MAX_PERIOD)
        period_input.setValue(self.parameters.period)
        hbox.addWidget(period_input)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Duty cycle: "))
        duty_cycle_input = QDoubleSpinBox()
        duty_cycle_input.setMinimum(self.generator.duty_cycle_step())
        duty_cycle_input.setMaximum(1.0)
        duty_cycle_input.setSingleStep(self.generator.duty_cycle_step())
        duty_cycle_input.setValue(self.parameters.duty_cycle)
        hbox.addWidget(duty_cycle_input)

        def period(value):
            self.parameters.period = value
            duty_cycle = duty_cycle_input.value()
            duty_cycle_input.setMinimum(self.generator.duty_cycle_step())
            duty_cycle_input.setSingleStep(self.generator.duty_cycle_step())
            duty_cycle_input.setValue(duty_cycle)

        period_input.valueChanged.connect(period)

        def duty_cycle(value):
            self.parameters.duty_cycle = value

        duty_cycle_input.valueChanged.connect(duty_cycle)

    def init_UI(self):
        vbox = QVBoxLayout(self)
        add_voltage_current_controls(self, vbox, self.generator)
        self._create_time_parameters(vbox)