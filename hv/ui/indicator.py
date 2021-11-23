from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QLCDNumber, QVBoxLayout


class Indicator(QGroupBox):
    def __init__(self, parent, units):
        super(Indicator, self).__init__(parent)
        self.units = units
        self.init_UI()

    def _create_indicator(self, name):
        hbox = QHBoxLayout()
        label = QLabel(name)
        display = QLCDNumber(7)
        display.setSegmentStyle(QLCDNumber.Flat)
        hbox.addWidget(display)
        hbox.addWidget(label)
        return hbox, display

    def init_UI(self):
        vbox = QVBoxLayout()
        hbox, self.voltage_display = self._create_indicator("Voltage, V")
        vbox.addLayout(hbox)
        hbox, self.current_display = self._create_indicator("Current, {}".format(self.units))
        vbox.addLayout(hbox)
        self.setLayout(vbox)