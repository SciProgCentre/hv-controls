import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QListWidget, QPushButton

from hv.hv_device import create_test_device, HVDevice
from hv.ui.widgets import HVItem


class DeviceList(QDockWidget):
    def __init__(self,parent,args):
        super().__init__("Device list", parent)
        self.init_UI(args)
        self.startTimer(60 * 1000, QtCore.Qt.VeryCoarseTimer)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        self.refresh()

    def add_fake_device(self):
        logging.root.info("Working with fake device")
        fake_device = create_test_device()
        HVItem(self.device_list, fake_device)

    def init_UI(self, args):
        widget = QWidget()
        vbox = QVBoxLayout()
        widget.setLayout(vbox)
        self.setWidget(widget)
        self.device_list = QListWidget(self)
        self.device_list.setMovement(0)

        if args.fake_device:
            self.add_fake_device()
        else:
            self.init_model()

        self.refresh_btn = QPushButton("Refresh\ndevice list")
        self.refresh_btn.clicked.connect(self.refresh)
        vbox.addWidget(self.refresh_btn)
        vbox.addWidget(self.device_list)


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