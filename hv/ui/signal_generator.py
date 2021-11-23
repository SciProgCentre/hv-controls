import dataclasses
from dataclasses import dataclass

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox

from hv.hv_device import HVDevice
from hv.ui.regulator import HVRegulator
from hv.ui.utils import HVWidgetSettings


class Generator(QObject):
    def __init__(self, name, device: HVDevice):
        super(Generator, self).__init__()
        self.name = name
        self.device = device


class GeneratorWidget(QWidget):
    def __init__(self,parent, generator: Generator):
        super(GeneratorWidget, self).__init__(parent)
        self.generator = generator

    def start(self):
        self.setDisabled(True)
        self.generator.start()

    def stop(self):
        self.setDisabled(False)
        self.generator.stop()

    def save_settings(self, settings: HVWidgetSettings):
        pass

@dataclass
class ScanningParameters:
    period : float
    duty_cycle : float
    voltage : float
    current: float


class ScanningGenerator(Generator):

    MIN_PERIOD = 0.5
    MIN_TICK = 0.1

    def __init__(self, name, device : HVDevice, parameters: ScanningParameters):
        super(ScanningGenerator, self).__init__(name, device)
        self.parameters = parameters

    def min_duty_cycle(self):
        return self.MIN_PERIOD / self.parameters.period

    def duty_cycle_step(self):
        return self.MIN_TICK / self.parameters.period

    def impulse_length(self):
        return self.parameters.period * self.parameters.duty_cycle


class ScanningWidget(GeneratorWidget):
    def __init__(self, parent, generator: ScanningGenerator):
        super(ScanningWidget, self).__init__(parent, generator)
        self.parameters = generator.parameters
        self.init_UI()

    def save_settings(self, settings: HVWidgetSettings):
        settings.generators[self.generator.name] = dataclasses.asdict(self.parameters)

    def _create_voltage(self):
        """Controls for setup voltage"""
        data = self.generator.device.data
        voltage_input = HVRegulator(self, "Voltage, V:", data.voltage_min, data.voltage_max,
                                    data.voltage_step, self.parameters.voltage)
        voltage_input.valueChanged.connect(lambda x: self.parameters.__setattr__("voltage", x))
        return voltage_input

    def _create_current(self):
        data = self.generator.device.data
        current_input = HVRegulator(self, "Limiting current, {}:".format(data.resolve_current_label()),
                                    data.current_min, data.current_max, data.resolve_current_step(),
                                    self.parameters.current)
        current_input.valueChanged.connect(lambda x: self.parameters.__setattr__("current", x))
        return current_input

    def _create_time_parameters(self, vbox):
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Period, s: "))
        period_input = QDoubleSpinBox()
        period_input.setMinimum(self.generator.MIN_PERIOD)
        period_input.setSingleStep(self.generator.MIN_TICK)
        period_input.setValue(self.parameters.period)
        hbox.addWidget(period_input)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Duty cycle: "))
        duty_cycle_input = QDoubleSpinBox()
        duty_cycle_input.setMinimum(self.generator.min_duty_cycle())
        duty_cycle_input.setSingleStep(self.generator.duty_cycle_step())
        duty_cycle_input.setValue(self.parameters.duty_cycle)
        hbox.addWidget(duty_cycle_input)

        def period(value):
            self.parameters.period = value

        period_input.valueChanged.connect(period)

        def duty_cycle(value):
            self.parameters.duty_cycle = value

        duty_cycle_input.valueChanged.connect(duty_cycle)


    def init_UI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        voltage_input = self._create_voltage()
        current_input = self._create_current()
        vbox.addWidget(voltage_input)
        vbox.addWidget(current_input)
        self._create_time_parameters(vbox)


class SquareWave(ScanningGenerator):
    def start(self):
        self.length = int(self.impulse_length()*1000)
        period = int(self.parameters.period*1000)
        self.timer_period = self.startTimer(period)

    def stop(self):
        self.killTimer(self.timer_period)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if a0.timerId() == self.timer_period:
            U, I = self.parameters.voltage, self.parameters.current
            self.device.set_value(U, I)
            self.device.update_value()
            QTimer.singleShot(self.length, self.device.reset_value)


def square_wave_widget(parent, device: HVDevice, settings):
    if "square_wave" in settings.generators:
        parameters = ScanningParameters(**settings.generators["square_vawe"])
    else:
        parameters = ScanningParameters(5, 0.5, device.data.voltage_min, device.data.current_min)
    generator = SquareWave("square_wave", device, parameters)
    return ScanningWidget(parent, generator)


GENERATOR_FACTORY = {
    "square wave" : square_wave_widget
}


class SignalGeneratorWidget(QWidget):

    def __init__(self, parent, device: HVDevice, settings: HVWidgetSettings):
        super(SignalGeneratorWidget, self).__init__(parent)
        self.state = False
        self.device = device
        self.settings = settings
        self.current_generator = GENERATOR_FACTORY[settings.last_generator](self, device, settings)
        self.init_UI()

    def change_generator(self, name):
        if not self.state:
            layout = self.layout()
            layout.removeWidget(self.current_generator)
            self.current_generator = GENERATOR_FACTORY[name](self,self.device, self.settings)
            self.layout().addWidget(self.current_generator)

    def init_UI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        button = QPushButton("Turn on\ngenerator")

        def turn():
            self.state = not self.state
            if self.state:
                button.setText("Turn off\ngenerator")
                self.current_generator.start()
            else:
                button.setText("Turn on\ngenerator")
                self.current_generator.stop()

        button.clicked.connect(turn)
        vbox.addWidget(button)
        generator_type = QComboBox(self)
        for i, key in enumerate(GENERATOR_FACTORY.keys()):
            generator_type.insertItem(i, key)
        vbox.addWidget(generator_type)

        generator_type.currentIndexChanged.connect(lambda x: self.change_generator(generator_type.itemText(x)))
        vbox.addWidget(self.current_generator)