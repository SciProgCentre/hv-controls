from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton


class Recorder(QWidget):
    def __init__(self, parent, filename):
        super(Recorder, self).__init__(parent)
        self.filename = filename
        self.state = False
        self.fout = None
        self.init_UI()

    def init_UI(self):
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        self.field = QLineEdit(self.filename, self)
        hbox.addWidget(self.field)

        def change_filename(new):
            self.filename = new

        self.field.textChanged.connect(change_filename)

        self.button = QPushButton("Start record", self)
        hbox.addWidget(self.button)
        def turn():
            self.state = not self.state
            if self.state:
                self.fout = open(self.filename, "a")
                self.button.setText("Stop record")
            else:
                self.fout.close()
                self.button.setText("Start record")

        self.button.clicked.connect(turn)

    def add_data(self, time, U, I):
        if self.state:
            self.fout.write("{},{},{}\n".format(time, U, I))
            self.fout.flush()