import argparse
import logging
import sys


def hv_controls_cmd(args):
    from hv.cmd_ui import HVShell
    HVShell(args).cmdloop()


def hv_controls_qt(args):
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("NPM Group")
    app.setApplicationName("HV-controls")
    from hv.qt_ui import HVWindow
    window = HVWindow(args)
    window.show()
    return sys.exit(app.exec_())


def create_parser():
    parser = argparse.ArgumentParser("HV-controls")
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--fake-device", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser


def app():
    args = create_parser().parse_args()

    if args.debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    if args.gui:
        hv_controls_qt(args)
    else:
        logging.basicConfig(filename = "hv-controls.log")
        hv_controls_cmd(args)
    return 0
