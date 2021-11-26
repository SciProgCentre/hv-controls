import dataclasses
import json
import logging
import os
import pathlib
from dataclasses import dataclass

from PyQt5 import QtCore
from PyQt5.QtWidgets import QPlainTextEdit, QDockWidget


def appdata():
    path = pathlib.Path(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation))
    if not path.exists():
        os.makedirs(path)
    return path


class QtLogging(logging.Handler):
    def __init__(self,parent, logger):
        super().__init__()
        self.widget = QDockWidget("Show log", parent)
        self._log_widget = QPlainTextEdit(self.widget)
        self._log_widget.setReadOnly(True)
        self.widget.setWidget(self._log_widget)
        self.records = []
        self.limit = 1000
        logger.addHandler(self)

    def emit(self, record):
        msg = self.format(record)
        if len(self.records) > self.limit:
            self.records = self.records[int(self.limit / 2):]
            self._log_widget.clear()
            self._log_widget.appendPlainText("\n".join(self.records))
        self.records.append(msg)
        self._log_widget.appendPlainText(msg)


@dataclass
class HVWidgetSettings:
    last_voltage: float
    last_current: float
    last_file: str = "data.csv"
    auto_reset: bool = True
    manual_mode: bool = True
    last_generator: str = "square wave"
    generators : dict = dataclasses.field(default_factory=dict)
    last_custom_generator_module: str = ""

    @staticmethod
    def load_settings(name, default_data):
        path = appdata() / "{}.json".format(name.replace("/", "_"))
        if path.exists():
            with path.open() as fin:
                settings = json.load(fin)
                return HVWidgetSettings(**settings)
        else:
            data = default_data
            return HVWidgetSettings(last_voltage=data.voltage_min, last_current=data.current_min,
                                    last_file="{}.csv".format(name.replace("/", "_")))

    @staticmethod
    def save_settings(name, settings):
        path = appdata() / "{}.json".format(name.replace("/", "_"))
        with path.open("w") as fout:
            json.dump(dataclasses.asdict(settings), fout)