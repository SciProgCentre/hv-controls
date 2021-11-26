import pathlib

from PyQt5.QtWidgets import QDockWidget, QTextBrowser


class Help(QDockWidget):
    def __init__(self, parent, file: pathlib.Path):
        super(Help, self).__init__("Help",parent)
        browser = QTextBrowser(self)
        self.setWidget(browser)
        with file.open("r") as fin:
            browser.setMarkdown(fin.read())
