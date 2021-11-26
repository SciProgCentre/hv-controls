import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QVBoxLayout

from hv.ui.indicator import Indicator
from hv.ui.oscilloscope import Oscilloscope
from hv.ui.recorder import Recorder
from hv.ui.source_setup import HVSourceSetup
from hv.ui.utils import HVWidgetSettings
from hv.ui.widgets import HVItem, AttentionLabel, ConnectionLostLabel


class HVWidget(QWidget):

    def __init__(self, parent, item: HVItem):
        super().__init__(parent)
        self.item = item
        self.settings = HVWidgetSettings.load_settings(str(self.item.device), self.item.device.data)
        self.init_UI()

    def _create_reset_box(self):
        check_box = QCheckBox("Autoreset voltage by exit", self)

        def handler(state):
            if state:
                self.attention_label.hide()
            else:
                self.attention_label.show()
            self.settings.auto_reset = state

        check_box.stateChanged.connect(handler)
        check_box.setChecked(self.settings.auto_reset)
        return check_box

    def init_UI(self):
        hbox = QHBoxLayout()
        self.setLayout(hbox)

        data = self.item.device.data

        vbox = QVBoxLayout()
        hbox.addLayout(vbox)
        self.attention_label = AttentionLabel()
        vbox.addWidget(self.attention_label)
        vbox.addWidget(self._create_reset_box(), QtCore.Qt.AlignLeft)
        self.indicator = Indicator(self, data.resolve_current_label())
        vbox.addWidget(self.indicator)
        self.record = Recorder(self, self.settings.last_file)
        vbox.addWidget(self.record)
        self.source_setup = HVSourceSetup(self, self.item.device, self.settings)
        vbox.addWidget(self.source_setup)
        self.connection_loss_label = ConnectionLostLabel()
        vbox.addWidget(self.connection_loss_label)
        vbox.addStretch()

        vbox = QVBoxLayout()
        hbox.addLayout(vbox)
        self._oscilloscope = Oscilloscope(self, data.resolve_current_label())
        vbox.addWidget(self._oscilloscope)
        vbox.addStretch()
        self.timer_id = self.startTimer(2000,  QtCore.Qt.PreciseTimer)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if self.item.device.is_open:
            self.read_values()
        else:
            # If loss connection to device, repeat connect
            self.connection_loss_label.show()
            self.item.device.open()
            if self.item.device.is_open:
                self.connection_loss_label.hide()

    def read_values(self):
        if self.item.device.is_open:
            I, U = self.item.device.get_IU()
            t = time.time()
            self.indicator.current_display.display(I)
            self.indicator.voltage_display.display(U)
            self._oscilloscope.update_data(t, U, I)
            i = I
            if self.item.device.data.current_units == "milli":
                i = i * 1000
            self.record.add_data(t, U, i)

    def closeTab(self):
        self.killTimer(self.timer_id)
        if self.settings.auto_reset:
            if self.item.device.is_open:
                self.item.device.reset_value()
        self.item.device.close()
        self.settings.last_file = self.record.filename
        self.settings.last_generator = self.source_setup.generator.current_generator.generator.name
        self.source_setup.generator.current_generator.save_settings(self.settings)
        HVWidgetSettings.save_settings(str(self.item.device), self.settings)