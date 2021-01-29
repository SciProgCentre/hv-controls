import sys
import pathlib
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListView, QPushButton, QTabWidget, QGroupBox, QDoubleSpinBox, \
    QLabel, QListWidget, QStyle, QLCDNumber

from hv.hv_device import HVDevice

ROOT_PATH = pathlib.Path(__file__).absolute().parent
RESOURCE_PATH = pathlib.Path(ROOT_PATH, "data")

class HVItem(QStandardItem):
    def __init__(self, device: HVDevice):
        super().__init__()
        self.device = device
        self.setData(device.data.name, 0)

class HVWidget(QtWidgets.QWidget):
    def __init__(self, item : HVItem):
        super().__init__()
        self.item = item
        self.init_UI()
        self.startTimer(1000)

    def init_UI(self):
        self.vbox = QVBoxLayout()

        # Controls for setup voltage
        self.setup_box = QGroupBox("Voltage setup")
        hbox = QHBoxLayout()
        self.voltage_input = QDoubleSpinBox()
        data = self.item.device.data
        self.voltage_input.setMinimum(data.voltage_min)
        self.voltage_input.setMaximum(data.voltage_max)
        self.voltage_input.setSingleStep(data.voltage_step)

        def apply():
            self.item.device.set_value(self.voltage_input.value())
            self.item.device.update_value()

        self.setup_btn = QPushButton("Aplly")
        self.setup_btn.clicked.connect(apply)
        hbox.addWidget(self.voltage_input)
        hbox.addWidget(self.setup_btn)
        self.setup_box.setLayout(hbox)
        self.vbox.addWidget(self.setup_box)

        # Controls for display indicator
        self.indicator_box = QGroupBox("Indicator")
        hbox = QHBoxLayout()

        # Controls for display voltage
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Voltage, V"))
        self.voltage_display = QLCDNumber()
        vbox.addWidget(self.voltage_display)
        hbox.addLayout(vbox)
        # Controls for display current
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Current, A"))
        self.current_display = QLCDNumber(7)
        vbox.addWidget(self.current_display)
        hbox.addLayout(vbox)

        self.indicator_box.setLayout(hbox)
        self.vbox.addWidget(self.indicator_box)
        self.vbox.addStretch()
        self.setLayout(self.vbox)


    def timerEvent(self, a0: 'QTimerEvent') -> None:
        I, U = self.item.device.get_IU()
        self.current_display.display(I)
        self.voltage_display.display(U)

    def closeTab(self):
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
        pass

    def open_device(self):
        indexes = self.device_list.selectedIndexes()
        for index in indexes:
            item = self.device_model.item(index.row(), index.column())
            widget = HVWidget(item)
            self.tabpane.addTab(widget)
            item.device.open()


class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.hbox = QHBoxLayout()
        self.tabpane = QTabWidget()
        self.tabpane.setTabsClosable(True)
        self.tabpane.tabCloseRequested.connect(self.closeTab)
        self.device_list = DeviceList(tabpane=self.tabpane)
        self.hbox.addWidget(self.device_list)
        self.hbox.addWidget(self.tabpane)


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
        self.setMinimumSize(640, 480)
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