from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QListWidgetItem

from hv.hv_device import HVDevice


class AttentionLabel(QLabel):
    def __init__(self, parent):
        super(AttentionLabel, self).__init__("Attention!\nHV device save last voltage!\nTake care of yourself!", parent)
        self.setStyleSheet("QLabel {color : red}")
        self.setAlignment(QtCore.Qt.AlignCenter)


class ConnectionLostLabel(QLabel):
    def __init__(self, parent):
        super(ConnectionLostLabel, self).__init__("Connection lost", parent)
        self.setStyleSheet("QLabel {color : red; font-size : 18pt}")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.hide()


class HVItem(QListWidgetItem):
    def __init__(self, list_widget, device: HVDevice):
        super().__init__(list_widget)
        self.device = device
        self.setData(0, device.data.name)


def update_style(widget):
    widget.style().unpolish(widget)
    widget.style().polish(widget)