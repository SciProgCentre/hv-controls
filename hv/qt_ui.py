import sys
import pathlib
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListView, QPushButton, QTabWidget, QGroupBox, QDoubleSpinBox, \
    QLabel, QListWidget, QStyle, QLCDNumber, QSlider

from hv.hv_device import HVDevice

ROOT_PATH = pathlib.Path(__file__).absolute().parent
RESOURCE_PATH = pathlib.Path(ROOT_PATH, "data")

class HVItem(QStandardItem):
    def __init__(self, device: HVDevice):
        super().__init__()
        self.device = device
        self.setData(device.data.name, 0)
        self.setEditable(False)

class HVWidget(QtWidgets.QWidget):
    def __init__(self, item : HVItem):
        super().__init__()
        self.item = item
        self.init_UI()
        self.timer_id = self.startTimer(2000)

    def _create_controls(self, name, min, max, step):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        spin_input = QDoubleSpinBox()
        data = self.item.device.data
        spin_input.setMinimum(min)
        spin_input.setMaximum(max)
        spin_input.setSingleStep(step)

        slider = QSlider()
        slider.setMaximum(int(min))
        slider.setMaximum(int(max))
        slider.setSingleStep(int(step))
        slider.setOrientation(QtCore.Qt.Horizontal)
        spin_input.valueChanged.connect(lambda x: slider.setValue(int(x)))
        slider.valueChanged.connect(lambda x: spin_input.setValue(x))

        vbox.addWidget(spin_input)
        vbox.addWidget(slider)
        label = QLabel(name)
        hbox.addWidget(label)
        hbox.addLayout(vbox)
        return hbox, spin_input

    def _create_controls_box(self):
        data = self.item.device.data
        # Controls for setup voltage
        setup_box = QGroupBox("Voltage setup")
        vbox = QVBoxLayout()
        hbox, voltage_input = self._create_controls("Voltage:",
                                                        data.voltage_min, data.voltage_max, data.voltage_step)
        vbox.addLayout(hbox)
        hbox, current_input = self._create_controls("Voltage:",
                                                        data.current_min, data.current_max, data.current_step)
        vbox.addLayout(hbox)

        def apply():
            self.item.device.set_value(
                voltage_input.value(),
                current_input.value()
            )
            self.item.device.update_value()

        setup_btn = QPushButton("Apply")
        setup_btn.clicked.connect(apply)
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(lambda : self.item.device.reset_value())
        hbox = QHBoxLayout()
        hbox.addWidget(setup_btn)
        hbox.addWidget(reset_btn)
        vbox.addLayout(hbox)
        setup_box.setLayout(vbox)
        return setup_box



    def init_UI(self):
        styleSheet  = "QLabel {font-size : 16pt}"
        self.vbox = QVBoxLayout()


        label = QLabel("Attenion!\nHV device save last voltage!\nTake care of yourself!")
        label.setStyleSheet("QLabel {color : red}")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.vbox.addWidget(label)
        # Controls for display indicator
        indicator_box = QGroupBox("Indicator")
        vbox = QVBoxLayout()
        # Controls for display voltage
        hbox = QHBoxLayout()
        label = QLabel("Voltage, V")
        label.setStyleSheet(styleSheet)
        self.voltage_display = QLCDNumber()
        self.voltage_display.setSegmentStyle(QLCDNumber.Flat)
        hbox.addWidget(self.voltage_display)
        hbox.addWidget(label)
        vbox.addLayout(hbox)
        # Controls for display current
        hbox = QHBoxLayout()
        label = QLabel("Current, {}".format(self.item.device.units_label))
        label.setStyleSheet(styleSheet)
        self.current_display = QLCDNumber(7)
        self.current_display.setSegmentStyle(QLCDNumber.Flat)
        self.current_display.resize(100, 100)
        hbox.addWidget(self.current_display)
        hbox.addWidget(label)
        vbox.addLayout(hbox)
        indicator_box.setLayout(vbox)
        self.vbox.addWidget(indicator_box)

        setup_box = self._create_controls_box()
        self.vbox.addWidget(setup_box)


        self.vbox.addStretch()

        self.setLayout(self.vbox)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        I, U = self.item.device.get_IU()
        self.current_display.display(I)
        self.voltage_display.display(U)

    def closeTab(self):
        self.killTimer(self.timer_id)
        self.item.device.close()


class DeviceList(QtWidgets.QWidget):
    def __init__(self, parent = None, tabpane = None):
        super().__init__(parent)
        self.used_devices = {}
        self.tabpane = tabpane
        self.device_model = QStandardItemModel()
        self.init_UI()
        self.init_model()

    def init_UI(self):
        self.vbox = QVBoxLayout()

        self.device_list = QListView(self)
        self.device_list.setMovement(0)
        self.device_list.setModel(self.device_model)
        self.open_btn = QPushButton("Open\nselected")
        self.refresh_btn = QPushButton("Update\ndevice\nlist")
        self.open_btn.clicked.connect(self.open_device)
        self.refresh_btn.clicked.connect(self.refresh)

        self.vbox.addWidget(self.device_list)
        self.vbox.addWidget(self.open_btn)
        self.vbox.addWidget(self.refresh_btn)

        self.setLayout(self.vbox)

    def init_model(self):
        for dev in HVDevice.find_all_devices():
            self.device_model.appendRow([HVItem(dev)])



    def refresh(self):
        """
        TODO(Update device list or realize subscription on new device)
        """
        n = self.device_model.rowCount()
        old = []
        for i in range(n):
            item = self.device_model.item(i,0)
            old.append(item.device)
        new = HVDevice.find_new_devices(old)
        for dev in new:
            self.device_model.appendRow([HVItem(dev)])

    def open_device(self):
        indexes = self.device_list.selectedIndexes()
        for index in indexes:
            item : HVItem = self.device_model.item(index.row(), index.column())
            widget = HVWidget(item)
            name = item.device.device.name
            dev_url = item.device.device.url
            self.tabpane.addTab(widget, "{}:{}".format(name, dev_url))
            item.device.open()


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setStyleSheet("* {font-size: 12pt}")
        self.hbox = QHBoxLayout()
        self.tabpane = QTabWidget()
        self.tabpane.setTabsClosable(True)
        self.tabpane.tabCloseRequested.connect(self.closeTab)
        self.device_list = DeviceList(tabpane=self.tabpane)
        self.hbox.addWidget(self.device_list, stretch=10)
        self.hbox.addWidget(self.tabpane, stretch=20)
        self.setLayout(self.hbox)


    def closeTab(self, index):
        widget = self.tabpane.widget(index)
        widget.closeTab()
        del widget


class HVWindow(QtWidgets.QMainWindow):

    ICON_PATH = pathlib.Path(RESOURCE_PATH, "basic_bolt.svg")

    def __init__(self, args):
        super().__init__()

        self.central = MainWidget()
        self.setCentralWidget(self.central)
        self.setMinimumSize(720, 480)
        self.setWindowTitle("HV-controls")
        self.setWindowIcon(QIcon(str(self.ICON_PATH)))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = HVWindow(sys.argv)
    window.show()
    sys.exit(app.exec_())
    return 0

if __name__ == '__main__':
    main()