import dataclasses
import itertools
import math
import pathlib
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QLabel, QDoubleSpinBox, \
    QLineEdit, QFileDialog

from hv.hv_device import HVDevice
from hv.ui.regulator import HVRegulator
from hv.ui.utils import HVWidgetSettings
import os

class Generator(QObject):

    abort_signal = pyqtSignal()

    MIN_PERIOD = 1.0
    MAX_PERIOD = MIN_PERIOD*1_000
    MIN_TICK = 0.2

    def __init__(self, name, device: HVDevice):
        super(Generator, self).__init__()
        self.name = name
        self.device = device

    def start(self):
        pass

    def stop(self):
        pass


class GeneratorWidget(QWidget):
    def __init__(self,parent, generator: Generator):
        super(GeneratorWidget, self).__init__(parent)
        self.generator = generator
        self.generator.abort_signal.connect(self.stop)

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
        period_input.setMaximum(self.generator.MAX_PERIOD)
        period_input.setValue(self.parameters.period)
        hbox.addWidget(period_input)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addWidget(QLabel("Duty cycle: "))
        duty_cycle_input = QDoubleSpinBox()
        duty_cycle_input.setMinimum(self.generator.min_duty_cycle())
        duty_cycle_input.setMaximum(1.0)
        duty_cycle_input.setSingleStep(self.generator.duty_cycle_step())
        duty_cycle_input.setValue(self.parameters.duty_cycle)
        hbox.addWidget(duty_cycle_input)

        def period(value):
            self.parameters.period = value
            duty_cycle = duty_cycle_input.value()
            duty_cycle_input.setMinimum(self.generator.min_duty_cycle())
            duty_cycle_input.setSingleStep(self.generator.duty_cycle_step())
            duty_cycle_input.setValue(duty_cycle)

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

    def __init__(self, device, parameters):
        super(SquareWave, self).__init__("square wave", device, parameters)

    def start(self):
        self.length = int(self.impulse_length()*1000)
        period = int(self.parameters.period*1000)
        self.timer_period = self.startTimer(period,  QtCore.Qt.PreciseTimer)

    def stop(self):
        self.killTimer(self.timer_period)
        # TODO(AUTORESET?)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if a0.timerId() == self.timer_period:
            if self.device.is_open:
                U, I = self.parameters.voltage, self.parameters.current
                self.device.set_value(U, I)
                self.device.update_value()
                QTimer.singleShot(self.length, self.device.reset_value)
            else:
                self.abort_signal.emit()


def square_wave_widget(parent, device: HVDevice, settings):
    if "square wave" in settings.generators:
        parameters = ScanningParameters(**settings.generators["square wave"])
    else:
        parameters = ScanningParameters(5, 0.5, device.data.voltage_min, device.data.current_min)
    generator = SquareWave(device, parameters)
    return ScanningWidget(parent, generator)

class RawtoothState(Enum):
    START = auto()
    RISE = auto()
    IMPULSE = auto()
    ZERO = auto()

class RawtoothWave(ScanningGenerator):

    def __init__(self, device, parameters):
        super(RawtoothWave, self).__init__("rawtooth wave", device, parameters)
        self.MIN_TICK = 0.5
        self.current_time = 0.0

    def start(self):
        voltage = self.parameters.voltage
        self.current_impulse_length = self.impulse_length()
        coeff = voltage / self.current_impulse_length
        self.current_time = 0.0
        self.voltage_step = self.MIN_TICK*coeff
        self.voltage_accuracy = 2*self.device.data.voltage_step
        self.voltage = self.parameters.voltage
        self.state = RawtoothState.START
        self.timer_id  = self.startTimer(self.MIN_TICK*1000, QtCore.Qt.PreciseTimer)

    def stop(self):
        self.killTimer(self.timer_id)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if self.device.is_open:
            self.current_time += self.MIN_TICK
            if self.state == RawtoothState.START:
                self.device.set_value(self.voltage, self.parameters.current)
                self.device.update_value()
                self.state = RawtoothState.RISE
            elif self.state == RawtoothState.ZERO:
                if self.current_time > self.parameters.period:
                    self.current_time = 0
                    self.voltage = self.parameters.voltage
                    self.state = RawtoothState.START
            else:
                if self.state == RawtoothState.RISE:
                    I, U = self.device.get_IU()
                    if U > self.voltage or math.isclose(U, self.voltage, abs_tol=self.voltage_accuracy):
                      self.state = RawtoothState.IMPULSE

                if self.state == RawtoothState.IMPULSE:
                    self.device.set_value(self.voltage, self.parameters.current)
                    self.device.update_value()
                    self.voltage -= self.voltage_step
                    if self.voltage < 0:
                        self.voltage = 0

                if self.current_time >= self.current_impulse_length:
                    self.state = RawtoothState.ZERO
                    if self.voltage > 0:
                        self.device.reset_value()
        else:
            self.abort_signal.emit()



def rawtooth_wave_widget(parent, device: HVDevice, settings):
    if "rawtooth wave" in settings.generators:
        parameters = ScanningParameters(**settings.generators["rawtooth wave"])
    else:
        parameters = ScanningParameters(5, 0.5, device.data.voltage_min, device.data.current_min)
    generator =RawtoothWave(device, parameters)
    return ScanningWidget(parent, generator)


class CustomGenerator(Generator):
    path : pathlib.Path = None

    def __init__(self, name, device: HVDevice):
        super(CustomGenerator, self).__init__(name, device)
        self.MIN_TICK = 0.5

    def start(self):
        if self.path is not None:
            from importlib.machinery import SourceFileLoader
            user = SourceFileLoader(self.path.stem, str(self.path)).load_module()
            self.period = user.PERIOD
            self.func = user.generator
            self.times = itertools.cycle([self.MIN_PERIOD*i for i in range(int(self.period/self.MIN_PERIOD))])
            self.timer = self.startTimer(self.MIN_TICK*1000, QtCore.Qt.PreciseTimer)

    def stop(self):
        self.killTimer(self.timer)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        U, I = self.func(next(self.times))
        print(U, I)
        if self.device.is_open:
            self.device.set_value(U, I)
            self.device.update_value()
        else:
            self.abort_signal.emit()



class CustomGeneratorWidget(GeneratorWidget):
    def __init__(self, parent, generator: CustomGenerator, settings: HVWidgetSettings):
        super(CustomGeneratorWidget, self).__init__(parent, generator)
        self.settings = settings
        generator.path = pathlib.Path(settings.last_custom_generator_module)
        self.init_UI()

    def init_UI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        field = QLineEdit(self.settings.last_custom_generator_module, self)
        vbox.addWidget(field)

        def change_filename(new):
            self.settings.last_custom_generator_module = new
            self.generator.path = pathlib.Path(new)

        field.textChanged.connect(change_filename)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        select_btn = QPushButton(self.style().standardIcon(self.style().SP_DirOpenIcon), "Select file", self)

        def select_name():
            name = QFileDialog.getOpenFileName(self, "Select file for generator")[0]
            if name is not None or name != "":
                field.setText(name)

        select_btn.clicked.connect(select_name)


        export_btn = QPushButton(self.style().standardIcon(self.style().SP_DialogSaveButton), "Export template", self)

        def export():
            name = QFileDialog.getSaveFileName(self, "Create new file with custom generator")[0]
            if name is not None or name != "":
                with open(name, "w") as fout:
                    fout.write("\n\nPERIOD = 1 # seconds\n\n")
                    fout.write("def generator(t):\n")
                    fout.write('    """\n')
                    fout.write('    t is current time in period, in seconds\n')
                    fout.write('    Return Voltage(t) in Volts,Current(t) in {}\n'
                               .format(self.generator.device.data.resolve_current_label()))
                    fout.write('    """\n')
                    fout.write("    return 0.0, 0.0\n")

        export_btn.clicked.connect(export)

        hbox.addWidget(export_btn)
        hbox.addWidget(select_btn)


GENERATOR_FACTORY = {
    "square wave" : square_wave_widget,
    "rawtooth wave" : rawtooth_wave_widget,
    "custom" : lambda parent, device , settings : CustomGeneratorWidget(parent, CustomGenerator("custom", device), settings)
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
            self.settings.last_generator = name
            self.current_generator.save_settings(self.settings)
            layout = self.layout()
            self.current_generator.hide()
            layout.removeWidget(self.current_generator)
            self.current_generator = GENERATOR_FACTORY[name](self,self.device, self.settings)
            layout.addWidget(self.current_generator)

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
        current_indx = 0
        for i, key in enumerate(GENERATOR_FACTORY.keys()):
            generator_type.insertItem(i, key)
            if self.settings.last_generator == key:
                current_indx = i
        vbox.addWidget(generator_type)
        generator_type.currentIndexChanged.connect(lambda x: self.change_generator(generator_type.itemText(x)))
        generator_type.setCurrentIndex(current_indx)
        vbox.addWidget(self.current_generator)