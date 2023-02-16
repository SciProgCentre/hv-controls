from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QSlider, QLabel


class HVRegulator(QWidget):

    valueChanged = Signal(float)

    def __init__(self, parent, name, min_input, max_input, step, default):
        super(HVRegulator, self).__init__(parent)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        spin_input = QDoubleSpinBox(self)
        spin_input.setMinimum(min_input)
        spin_input.setMaximum(max_input)
        spin_input.setSingleStep(step)
        self.input = spin_input
        spin_input.valueChanged.connect(lambda x: self.valueChanged.emit(x))
        slider = QSlider(self)
        slider.setRange(int(min_input / step), int(max_input / step))
        slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider = slider
        self.slider_step = step
        spin_input.valueChanged.connect(lambda x: slider.setValue(int(x / step)))
        slider.valueChanged.connect(lambda x: spin_input.setValue(x * step))
        spin_input.setValue(default)
        vbox.addWidget(spin_input)
        vbox.addWidget(slider)
        self.label = QLabel(name, self)
        hbox.addWidget(self.label)
        hbox.addLayout(vbox)
        self.setLayout(hbox)

    def set_maximum(self, value):
        self.slider.setMaximum(int(value/self.slider_step))
        self.input.setMaximum(value)

    def value(self):
        return self.input.value()