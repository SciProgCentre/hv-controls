from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from hv.hv_device import HVDevice
from hv.ui.regulator import HVRegulator


class HVBasicSetup(QWidget):
    def __init__(self, parent, device: HVDevice, settings):
        super(HVBasicSetup, self).__init__(parent)
        self.device = device
        self.settings = settings
        self.init_UI()

    def _create_voltage(self):
        """Controls for setup voltage"""
        data = self.device.data
        voltage_input = HVRegulator(self, "Voltage, V:", data.voltage_min, data.voltage_max,
                                    data.voltage_step, self.settings.last_voltage)
        voltage_input.valueChanged.connect(lambda x: self.settings.__setattr__("last_voltage", x))
        return voltage_input

    def _create_current(self):
        data = self.device.data
        current_input = HVRegulator(self, "Limiting current, {}:".format(data.resolve_current_label()),
                                    data.current_min, data.current_max, data.resolve_current_step(),
                                    self.settings.last_current)
        current_input.valueChanged.connect(lambda x: self.settings.__setattr__("last_current", x))
        return current_input

    def init_UI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        voltage_input = self._create_voltage()
        current_input = self._create_current()
        vbox.addWidget(voltage_input)
        vbox.addWidget(current_input)

        def setup():
            if self.device.is_open:
                self.device.set_value(
                    voltage_input.value(),
                    current_input.value()
                )

        def apply():
            if self.device.is_open:
                setup()
                self.device.update_value()

        setup_and_turn_on = QPushButton("Setup&&Turn on")
        setup_and_turn_on.clicked.connect(apply)
        setup_btn = QPushButton("Setup")
        setup_btn.clicked.connect(setup)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda: self.device.reset_value() if self.device.is_open else None)

        hbox = QHBoxLayout()
        hbox.addWidget(setup_and_turn_on)
        hbox.addWidget(setup_btn)
        hbox.addWidget(reset_btn)
        vbox.addLayout(hbox)