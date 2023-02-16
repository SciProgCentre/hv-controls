from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout

from hv.hv_device import HVDevice
from hv.ui.basic_setup import HVBasicSetup
from hv.ui.signal_generator import SignalGeneratorWidget
from hv.ui.utils import HVWidgetSettings


class HVSourceSetup(QGroupBox):
    def __init__(self, parent, device: HVDevice, settings: HVWidgetSettings):
        super(HVSourceSetup, self).__init__(parent)
        self.device = device
        self.settings = settings
        self.init_UI()

    def _create_switch_button(self):
        text_manual = "Switch to \ngenerator mode"
        text_generator = "Switch to \nmanual mode"
        text_default = text_manual if self.settings.manual_mode else text_generator
        btn = QPushButton(text_default, self)

        def turn():
            self.settings.manual_mode = not self.settings.manual_mode
            if self.settings.manual_mode:
                btn.setText(text_manual)
                self.generator.hide()
                self.basic_setup.show()
            else:
                self.generator.show()
                self.basic_setup.hide()
                btn.setText(text_generator)

        btn.clicked.connect(turn)
        return btn

    def init_UI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        switch_btn = self._create_switch_button()
        vbox.addWidget(switch_btn)

        self.generator = SignalGeneratorWidget(self, self.device, self.settings)
        self.basic_setup = HVBasicSetup(self, self.device, self.settings)
        if self.settings.manual_mode:
            self.generator.hide()
        else:
            self.basic_setup.hide()
        vbox.addWidget(self.generator)
        vbox.addWidget(self.basic_setup)

        self.generator.state_signal.connect(lambda x: switch_btn.setDisabled(x))