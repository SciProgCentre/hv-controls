import sys
import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTextEdit, QWidget, QHBoxLayout, QApplication, QMainWindow


class TimerWidget(QTextEdit):
    def __init__(self, parent, period, sleep = None):
        super(TimerWidget, self).__init__(parent)
        self.setReadOnly(True)
        self.sleep = sleep
        self.init_time = time.perf_counter_ns()
        self.timer = self.startTimer(period, QtCore.Qt.PreciseTimer)

    def timerEvent(self, e: QtCore.QTimerEvent) -> None:
        self.append("{:.2f}".format((time.perf_counter_ns() - self.init_time) / 1_000_000))
        if self.sleep is not None:
            time.sleep(self.sleep)

class Widget(QWidget):
    def __init__(self,parent):
        super(Widget, self).__init__(parent)
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        w1 = TimerWidget(parent, 2000, 0.2)
        w2 = TimerWidget(parent, 500)
        hbox.addWidget(w1)
        hbox.addWidget(w2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = QMainWindow()
    main.setBaseSize(600, 800)
    w = Widget(main)
    main.setCentralWidget(w)
    main.show()
    app.exec_()