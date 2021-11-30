import itertools
import pathlib

from PyQt5 import QtCore
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QFileDialog

from hv.hv_device import HVDevice
from hv.ui.generators import Generator, GeneratorWidget

TEMPLATE_GENERATOR = """import math


PERIOD = 1.0 # seconds, 


def generator(t):
    \"\"\"
    t is current time in period, in seconds
    Return Voltage(t) in Volts, Limiting Current(t) in microAmpers
    \"\"\"
    return 0.0, 0.0
"""

class CustomGenerator(Generator):
    NAME = "custom"
    path : pathlib.Path = None

    def __init__(self, device: HVDevice):
        super(CustomGenerator, self).__init__(device)

    def start(self):
        if self.path is not None:
            self._last_voltage = None
            self._last_current = None
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
        if self.device.is_open:
            if self.device.data.current_units == "milli":
                I = I / 1000
            if self._last_current != I or self._last_voltage != U:
                self.setup(U, I)
                self._last_current = I
                self._last_voltage = U
        else:
            self.abort_signal.emit()


class CustomGeneratorWidget(GeneratorWidget):
    def __init__(self, parent, generator: CustomGenerator):
        super(CustomGeneratorWidget, self).__init__(parent, generator)
        self.settings = QSettings()
        self.init_UI()

    def init_UI(self):
        vbox = QVBoxLayout(self)
        field = QLineEdit(self)
        vbox.addWidget(field)

        def change_filename(new):
            if new != "":
                self.generator.path = pathlib.Path(new)

        field.textChanged.connect(change_filename)
        field.setText(self.settings.value("file", ""))
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
                    fout.write(TEMPLATE_GENERATOR)

        export_btn.clicked.connect(export)
        hbox.addWidget(export_btn)
        hbox.addWidget(select_btn)