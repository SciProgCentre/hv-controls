import logging
import pathlib

import jinja2
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtHelp import QHelpEngine
from PyQt5.QtWidgets import QMainWindow, QDockWidget
from PySide2.QtGui import QFontDatabase

from hv.ui.central_widget import HVCentralWidget
from hv.ui.device_list import DeviceList
from hv.ui.help import Help
from hv.ui.utils import QtLogging
from hv.ui.widgets import HVItem

ROOT_PATH = pathlib.Path(__file__).absolute().parent
RESOURCE_PATH = pathlib.Path(ROOT_PATH, "data")


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
    HELP_PATH = RESOURCE_PATH / "help.md"

    def __init__(self, args):
        super().__init__()
        self.qt_logging = QtLogging(self, logging.root)
        self.setMinimumSize(1280, 720)
        self.setWindowTitle("HV-controls")
        self.setWindowIcon(QIcon(str(self.ICON_PATH)))
        self.init_UI(args)


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

        central = HVCentralWidget(self)

        def open_device(index):
            item: HVItem = device_list.device_list.item(index.row())
            central.open_device(item)

        device_list.device_list.doubleClicked.connect(open_device)
        self.setCentralWidget(central)

        help = Help(self, self.HELP_PATH)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, help)
        help.setVisible(False)
        toolbar.addAction(help.toggleViewAction())


