import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QListView, QPushButton



class HVWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

class DeviceList(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.deviceList = QListView()
        self.vbox = QVBoxLayout()
        self.open_btn = QPushButton("Open\nselected")
        self.refresh_btn = QPushButton("Update\ndevice\nlist")
        self.vbox.addWidget(self.open_btn)
        self.vbox.addWidget(self.refresh_btn)
        self.vbox.addStretch()
        self.hbox.addWidget(self.deviceList)
        self.hbox.addLayout(self.vbox)
        self.setLayout(self.hbox)

    def refresh(self):
        pass

    def open_device(self):
        pass

class HVWindow(QtWidgets.QMainWindow):
    def __init__(self, args):
        super().__init__()

        self.central = DeviceList()
        self.setCentralWidget(self.central)
        self.setMinimumSize(640, 480)







def main():
    app = QtWidgets.QApplication(sys.argv)
    window = HVWindow(sys.argv)
    window.show()
    sys.exit(app.exec_())
    return 0

if __name__ == '__main__':
    main()