import dataclasses
import json
import logging
import os
import pathlib
import time
from dataclasses import dataclass

from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QTabWidget, QGroupBox, QDoubleSpinBox, \
    QLabel, QListWidget, QLCDNumber, QSlider, QListWidgetItem, QWidget, QMainWindow, QPlainTextEdit, QAction, \
    QCheckBox

from hv.hv_device import HVDevice, create_test_device

ROOT_PATH = pathlib.Path(__file__).absolute().parent
RESOURCE_PATH = pathlib.Path(ROOT_PATH, "data")


def appdata():
    path = pathlib.Path(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation))
    if not path.exists():
        os.makedirs(path)
    return path


class HVItem(QListWidgetItem):
    def __init__(self, list_widget, device: HVDevice):
        super().__init__(list_widget)
        self.device = device
        self.setData(0, device.data.name)


class AttentionLabel(QLabel):
    def __init__(self):
        super(AttentionLabel, self).__init__("Attention!\nHV device save last voltage!\nTake care of yourself!")
        self.setStyleSheet("QLabel {color : red}")
        self.setAlignment(QtCore.Qt.AlignCenter)


class ConnectionLostLabel(QLabel):
    def __init__(self):
        super(ConnectionLostLabel, self).__init__("Connection lost")
        self.setStyleSheet("QLabel {color : red; font-size : 18pt}")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.hide()


@dataclass
class HVWidgetSettings:
    last_voltage: float
    last_current: float
    auto_reset: bool = True


class HVWidget(QWidget):
    style_sheet = "QLabel {font-size : 16pt}"

    def __init__(self, item: HVItem):
        super().__init__()
        self.item = item
        self.settings = self.load_settings()
        self.init_UI()

    def load_settings(self):
        path = appdata() / "{}.json".format(self.item.device)
        if path.exists():
            with path.open() as fin:
                settings = json.load(fin)
                return HVWidgetSettings(**settings)
        else:
            data = self.item.device.data
            return HVWidgetSettings(last_voltage=data.voltage_min, last_current=data.current_min)

    def save_settings(self):
        path = appdata() / "{}.json".format(self.item.device)
        with path.open("w") as fout:
            json.dump(dataclasses.asdict(self.settings), fout)

    def _create_controls(self, name, min_input, max_input, step, default):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        spin_input = QDoubleSpinBox()
        spin_input.setMinimum(min_input)
        spin_input.setMaximum(max_input)
        spin_input.setSingleStep(step)

        slider = QSlider()
        slider.setRange(int(min_input / step), int(max_input / step))
        slider.setOrientation(QtCore.Qt.Horizontal)

        spin_input.valueChanged.connect(lambda x: slider.setValue(int(x / step)))
        slider.valueChanged.connect(lambda x: spin_input.setValue(x * step))
        spin_input.setValue(default)
        vbox.addWidget(spin_input)
        vbox.addWidget(slider)
        label = QLabel(name)
        label.setStyleSheet(self.style_sheet)
        hbox.addWidget(label)
        hbox.addLayout(vbox)
        return hbox, spin_input

    def _create_controls_box(self):
        data = self.item.device.data
        # Controls for setup voltage
        setup_box = QGroupBox()
        vbox = QVBoxLayout()
        hbox, voltage_input = self._create_controls("Voltage, V:", data.voltage_min, data.voltage_max,
                                                    data.voltage_step, self.settings.last_voltage)
        voltage_input.valueChanged.connect(lambda x: self.settings.__setattr__("last_voltage", x))
        vbox.addLayout(hbox)

        if data.current_units == "micro":
            current_step = data.current_step
        elif data.current_units == "milli":
            current_step = data.current_step / 1000
        else:
            current_step = data.current_step

        hbox, current_input = self._create_controls("Limiting current, {}:".format(data.resolve_current_label()),
                                                    data.current_min, data.current_max, current_step,
                                                    self.settings.last_current)
        vbox.addLayout(hbox)
        current_input.valueChanged.connect(lambda x: self.settings.__setattr__("last_current", x))

        def setup():
            if self.item.device.is_open:
                self.item.device.set_value(
                    voltage_input.value(),
                    current_input.value()
                )

        def apply():
            if self.item.device.is_open:
                setup()
                self.item.device.update_value()

        setup_and_turn_on = QPushButton("Setup&&Turn on")
        setup_and_turn_on.clicked.connect(apply)
        setup_btn = QPushButton("Setup")
        setup_btn.clicked.connect(setup)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda: self.item.device.reset_value() if self.item.device.is_open else None)

        hbox = QHBoxLayout()
        hbox.addWidget(setup_and_turn_on)
        hbox.addWidget(setup_btn)
        hbox.addWidget(reset_btn)
        vbox.addLayout(hbox)
        setup_box.setLayout(vbox)
        return setup_box

    def _create_indicator(self, name):
        hbox = QHBoxLayout()
        label = QLabel(name)
        label.setStyleSheet(self.style_sheet)
        display = QLCDNumber(7)
        display.setSegmentStyle(QLCDNumber.Flat)
        hbox.addWidget(display)
        hbox.addWidget(label)
        return hbox, display

    def _create_indicator_box(self):
        indicator_box = QGroupBox()
        vbox = QVBoxLayout()
        hbox, self.voltage_display = self._create_indicator("Voltage, V")
        vbox.addLayout(hbox)
        hbox, self.current_display = self._create_indicator("Current, {}".format(self.item.device.units_label))
        vbox.addLayout(hbox)
        indicator_box.setLayout(vbox)
        self.update_display()
        self.timer_id = self.startTimer(2000)
        return indicator_box

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
        vbox = QVBoxLayout()
        self.attention_label = AttentionLabel()
        vbox.addWidget(self.attention_label)
        vbox.addWidget(self._create_reset_box(), QtCore.Qt.AlignLeft)
        vbox.addWidget(self._create_indicator_box())
        vbox.addWidget(self._create_controls_box())
        self.connection_loss_label = ConnectionLostLabel()
        vbox.addWidget(self.connection_loss_label)
        vbox.addStretch()
        self.setLayout(vbox)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if self.item.device.is_open:
            self.update_display()
        else:
            # If loss connection to device, repeat connect
            self.connection_loss_label.show()
            self.item.device.open()
            if self.item.device.is_open:
                self.connection_loss_label.hide()

    def update_display(self):
        if self.item.device.is_open:
            I, U = self.item.device.get_IU()
            self.current_display.display(I)
            self.voltage_display.display(U)

    def closeTab(self):
        self.killTimer(self.timer_id)
        if self.settings.auto_reset:
            if self.item.device.is_open:
                self.item.device.reset_value()
        self.item.device.close()
        self.save_settings()


class DeviceList(QWidget):
    def __init__(self, tabpane, auto_init=True, parent=None):
        super().__init__(parent)
        self.tabpane = tabpane
        self.init_UI(auto_init)
        self.startTimer(60 * 1000, QtCore.Qt.VeryCoarseTimer)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        self.refresh()

    def add_fake_device(self):
        logging.root.info("Working with fake device")
        fake_device = create_test_device()
        HVItem(self.device_list, fake_device)

    def init_UI(self, auto_init):
        self.vbox = QVBoxLayout()
        self.device_list = QListWidget(self)
        self.device_list.setMovement(0)
        self.device_list.doubleClicked.connect(self.open_device)
        if auto_init:
            self.init_model()

        self.refresh_btn = QPushButton("Refresh\ndevice list")
        self.refresh_btn.clicked.connect(self.refresh)
        self.vbox.addWidget(self.refresh_btn)
        self.vbox.addWidget(self.device_list)
        self.setLayout(self.vbox)

    def init_model(self):
        for dev in HVDevice.find_all_devices():
            HVItem(self.device_list, dev)

    def refresh(self):
        old = []
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            old.append(item.device)
        new = HVDevice.find_new_devices(old)
        for dev in new:
            HVItem(self.device_list, dev)

    def open_device(self, index):
        item: HVItem = self.device_list.item(index.row())
        widget = HVWidget(item)
        name = item.device.device.name
        dev_url = item.device.device.url
        self.tabpane.addTab(widget, "{}\n{}".format(name, dev_url))
        item.device.open()


class QtLogging(logging.Handler):
    def __init__(self, logger):
        super().__init__()
        self.widget = QPlainTextEdit()
        self.widget.setReadOnly(True)
        self.widget.setWindowTitle("Log")
        self.records = []
        self.limit = 1000
        logger.addHandler(self)

    def emit(self, record):
        msg = self.format(record)
        if len(self.records) > self.limit:
            self.records = self.records[int(self.limit / 2):]
            self.widget.clear()
            self.widget.appendPlainText("\n".join(self.records))
        self.records.append(msg)
        self.widget.appendPlainText(msg)


class MainWidget(QWidget):
    def __init__(self, args, parent=None):
        super().__init__(parent)
        self.setStyleSheet("* {font-size: 12pt}")
        self.init_UI(args)

    def init_UI(self, args):
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        tabpane = QTabWidget(self)
        tabpane.setTabsClosable(True)

        def close_tab(index):
            widget = tabpane.widget(index)
            widget.closeTab()
            tabpane.removeTab(index)
            del widget

        tabpane.tabCloseRequested.connect(close_tab)
        device_list = DeviceList(tabpane, auto_init=not args.fake_device, parent=self)
        hbox.addWidget(device_list, stretch=10)
        hbox.addWidget(tabpane, stretch=20)
        if args.fake_device:
            device_list.add_fake_device()


class HVWindow(QMainWindow):
    ICON_PATH = RESOURCE_PATH / "basic_bolt.svg"

    def __init__(self, args):
        super().__init__()
        self.qt_logging = QtLogging(logging.root)
        self.central = MainWidget(args)
        self.setCentralWidget(self.central)
        self.setMinimumSize(720, 480)
        self.setWindowTitle("HV-controls")
        self.setWindowIcon(QIcon(str(self.ICON_PATH)))
        self.init_toolbar()

    def init_toolbar(self):
        toolbar = self.addToolBar('Toolbar')
        action = QAction("Show log", self)

        def open_log():
            self.qt_logging.widget.show()

        action.triggered.connect(open_log)
        toolbar.addAction(action)
