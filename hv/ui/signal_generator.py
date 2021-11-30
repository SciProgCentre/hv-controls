from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QCheckBox

from hv.hv_device import HVDevice
from hv.ui.generators import GENERATOR_FACTORY
from hv.ui.utils import HVWidgetSettings


class SignalGeneratorWidget(QWidget):

    state_signal = pyqtSignal(bool)

    def _turn(self):
        self.state = not self.state
        self.state_signal.emit(self.state)

    def __init__(self, parent, device: HVDevice, settings: HVWidgetSettings):
        super(SignalGeneratorWidget, self).__init__(parent)
        self.state = False
        self.device = device
        self.settings = settings
        parameters = settings.resolve_generators(settings.last_generator)
        self.current_generator = GENERATOR_FACTORY[settings.last_generator](self, device, parameters)
        self.init_UI()

    def change_generator(self, name):
        if not self.state:
            self.settings.last_generator = name
            self.settings.update_generators(self.current_generator.export_settings())
            parameters = self.settings.resolve_generators(name)
            layout = self.layout()
            self.current_generator.hide()
            layout.removeWidget(self.current_generator)
            self.current_generator = GENERATOR_FACTORY[name](self, self.device, parameters)
            layout.addWidget(self.current_generator)
            self.current_generator.generator.abort_signal.connect(self._turn)

    def _create_reset(self):
        auto_reset_box = QCheckBox("Autoreset generator", self)
        auto_reset_box.setChecked(self.settings.auto_reset_generator)

        def handler(state):
            self.settings.auto_reset = state

        auto_reset_box.stateChanged.connect(handler)
        return auto_reset_box


    def init_UI(self):
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        button = QPushButton("Turn on\ngenerator")
        button.clicked.connect(self._turn)
        generator_type = QComboBox(self)
        current_indx = 0
        for i, key in enumerate(GENERATOR_FACTORY.keys()):
            generator_type.insertItem(i, key)
            if self.settings.last_generator == key:
                current_indx = i


        vbox_1 = QVBoxLayout()
        vbox_1.addWidget(generator_type)
        vbox_1.addWidget(self._create_reset())
        hbox.addLayout(vbox_1, 1)
        hbox.addWidget(button, 1)

        generator_type.currentIndexChanged.connect(lambda x: self.change_generator(generator_type.itemText(x)))
        generator_type.setCurrentIndex(current_indx)
        vbox.addWidget(self.current_generator)

        def turn(state):
            generator_type.setDisabled(state)
            if state:
                button.setText("Turn off\ngenerator")
                self.current_generator.start()
            else:
                button.setText("Turn on\ngenerator")
                self.current_generator.stop()
                if self.settings.auto_reset_generator:
                    self.device.reset_value()

        self.state_signal.connect(turn)