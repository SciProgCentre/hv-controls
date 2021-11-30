import logging
import pathlib

import jinja2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSettings, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QDockWidget, QTextBrowser
from PyQt5.QtGui import QFontDatabase

from hv.ui.central_widget import HVCentralWidget
from hv.ui.device_list import DeviceList, DeviceInfo
from hv.ui.utils import QtLogging
from hv.ui.widgets import HVItem

ROOT_PATH = pathlib.Path(__file__).absolute().parent
RESOURCE_PATH = pathlib.Path(ROOT_PATH, "resources")


def materials_theme():
    fonts_path = RESOURCE_PATH / 'fonts' / 'roboto'
    for font in fonts_path.iterdir():
        if font.suffix == '.ttf':
            QFontDatabase.addApplicationFont(str(font))

    loader = jinja2.FileSystemLoader(RESOURCE_PATH)
    env = jinja2.Environment(autoescape=False, loader=loader)
    stylesheet = env.get_template("material.css")

    theme = {
        "font_family": "Roboto",
        "font_size" : "12pt"
    }
    return stylesheet.render(**theme)


class HVWindow(QMainWindow):
    ICON_PATH = RESOURCE_PATH / "basic_bolt.svg"
    HELP_PATH = RESOURCE_PATH / "help.html"

    def __init__(self, args):
        super().__init__()
        self.setWindowTitle("HV-controls")
        self.setWindowIcon(QIcon(str(self.ICON_PATH)))
        self.qt_logging = QtLogging(self, logging.root)
        self.settings = QSettings()
        self.init_size()
        self.init_UI(args)

    def init_size(self):
        desktop = QDesktopWidget()
        size = desktop.availableGeometry().size()
        width = min(size.width(), 1280)
        height = min(size.height(), 720)
        size =QSize(width, height)
        size = self.settings.value("window_size", size)
        self.resize(size)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.settings.setValue("window_size", self.size())
        self.centralWidget().closeEvent(event)
        super(HVWindow, self).closeEvent(event)

    def init_UI(self, args):
        toolbar = self.addToolBar("Toolbar")
        toolbar.setAllowedAreas(QtCore.Qt.LeftToolBarArea)
        toolbar.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        device_list = DeviceList(self, args)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, device_list)
        toolbar.addAction(device_list.toggleViewAction())
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.qt_logging.widget)
        self.qt_logging.widget.setVisible(False)
        toolbar.addAction(self.qt_logging.widget.toggleViewAction())
        device_info = DeviceInfo(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, device_info)
        device_info.setVisible(False)
        toolbar.addAction(device_info.toggleViewAction())


        central = HVCentralWidget(self)
        self.setCentralWidget(central)

        def open_device(index):
            item: HVItem = device_list.device_list.item(index.row())
            central.open_device(item)

        device_list.device_list.doubleClicked.connect(open_device)

        def select_device():
            items = device_list.device_list.selectedItems()
            if len(items) != 0:
                device_info.update_info(items[0].device)

        device_list.device_list.itemSelectionChanged.connect(select_device)



        help = Help(self, self.HELP_PATH)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, help)
        help.setVisible(False)
        toolbar.addAction(help.toggleViewAction())


class Help(QDockWidget):
    def __init__(self, parent, file: pathlib.Path):
        super(Help, self).__init__("Help",parent)
        browser = QTextBrowser(self)
        self.setWidget(browser)
        with file.open("r") as fin:
            browser.setHtml(fin.read())
