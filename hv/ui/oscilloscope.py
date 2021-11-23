import time

import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import (FigureCanvas,  NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class Oscilloscope(QWidget):
    N = 300

    def __init__(self, parent, current_units):
        super(Oscilloscope, self).__init__(parent)
        self.current_units = current_units
        self.state = True
        self.init_data()
        self.init_UI()

    def init_data(self):
        self.init_time = time.time()
        self.times = list(np.linspace(self.init_time - self.N, self.init_time, self.N, endpoint=True))
        self.voltage = [0 for i in self.times]
        self.current = [0 for i in self.times]

    def init_UI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self._figure = Figure(figsize=(7, 5))
        dynamic_canvas = FigureCanvas(self._figure)
        vbox.addWidget(NavigationToolbar(dynamic_canvas, self))
        vbox.addWidget(dynamic_canvas)
        self._voltage_ax, self._current_ax = dynamic_canvas.figure.subplots(2, 1)

        self._voltage_ax.set_ylabel("Voltage, kV", fontsize = 16)

        self._current_ax.set_xlabel("Time, s", fontsize = 16)
        self._current_ax.set_ylabel("Current, {}".format(self.current_units), fontsize = 16)

        for axes in [self._voltage_ax, self._current_ax]:
            axes.grid(True)
            axes.minorticks_on()
            axes.tick_params(axis="y",which="both", right=True, labelright=True)

        self._voltage_line = self._voltage_ax.plot(np.asarray(self.times) - self.init_time, self.voltage)[0]
        self._current_line = self._current_ax.plot(np.asarray(self.times) - self.init_time, self.current)[0]
        self._figure.tight_layout()

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        stop_btn = QPushButton("Stop")

        def turn():
            self.state = not self.state
            if self.state:
                stop_btn.setText("Stop")
            else:
                stop_btn.setText("Continue")

        stop_btn.clicked.connect(turn)
        hbox.addWidget(stop_btn)

        save_btn = QPushButton("Save buffer")
        hbox.addWidget(save_btn)

        def save():
            name = QFileDialog.getSaveFileName(self, "Save oscilloscope buffer.")
            with open(name[0], "w") as fout:
                fout.write('"{}","{}","{}"\n'.format("Unix time, s", "Voltage, kV", "Current, {}".format(self.current_units)))
                for time, U, I in zip(self.times, self.voltage, self.current):
                    fout.write("{},{},{}\n".format(time, U, I))

        save_btn.clicked.connect(save)

    def update_data(self, time, U, I):
        if self.state:
            self.times.pop(0)
            self.voltage.pop(0)
            self.current.pop(0)
            self.times.append(time)
            self.voltage.append(U/1000) # to kilovolts
            self.current.append(I)
            self._update_canvas()

    def _update_axes(self, line, axes, x0, x, y):
        line.set_data(np.asarray(x) - x0, np.asarray(y))
        axes.relim()
        axes.autoscale()

    def _update_canvas(self):
        self._update_axes(self._voltage_line, self._voltage_ax, self.init_time, self.times, self.voltage)
        self._update_axes(self._current_line, self._current_ax, self.init_time, self.times, self.current)
        self._figure.tight_layout()
        self._figure.canvas.draw()