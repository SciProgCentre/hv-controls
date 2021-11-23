from PyQt5.QtWidgets import QTabWidget

from hv.ui.hv_widget import HVWidget
from hv.ui.widgets import HVItem


class HVCentralWidget(QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def open_device(self, item: HVItem):
        widget = HVWidget(self, item)
        self.addTab(widget, str(item.device))
        item.device.open()

    def close_tab(self, index):
        widget = self.widget(index)
        widget.closeTab()
        self.removeTab(index)
        del widget