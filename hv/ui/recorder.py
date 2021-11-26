from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog


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
        save_btn = QPushButton(self.style().standardIcon(self.style().SP_DirOpenIcon),"", self)
        hbox.addWidget(save_btn)

        field = QLineEdit(self.filename, self)
        hbox.addWidget(field)

        def change_filename(new):
            self.filename = new

        field.textChanged.connect(change_filename)

        def select_name():
            name = QFileDialog.getSaveFileName(self, "Create/Select file for record")[0]
            if name is not None or name != "":
                field.setText(name)

        save_btn.clicked.connect(select_name)

        button = QPushButton("Start record", self)
        hbox.addWidget(button)

        def turn():
            self.state = not self.state
            if self.state:
                self.fout = open(self.filename, "a")
                button.setText("Stop record")
            else:
                self.fout.close()
                button.setText("Start record")

        button.clicked.connect(turn)

    def add_data(self, time, U, I):
        if self.state:
            self.fout.write("{},{},{}\n".format(time, U, I))
            self.fout.flush()
