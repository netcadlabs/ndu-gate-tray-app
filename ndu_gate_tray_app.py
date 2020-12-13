import enum
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog

from ndu_gate_service_wrapper import ServiceWrapper


class ServiceState(enum.Enum):
    Started = 1
    Stopped = 2


class NDUGateTrayApplication(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'NDU Gate Camera Service - 0.1.8')

        self._init_ui(parent)

        self.activated.connect(self.on_tray_icon_activated)

        self.service = ServiceWrapper()
        self.config_file = None
        self.state = ServiceState.Stopped

    def _init_ui(self, parent):
        self.menu = QtWidgets.QMenu(parent)

        self.config_action = self.menu.addAction("Set Config")
        self.config_action.triggered.connect(self.set_config)
        self.config_action.setIcon(QtGui.QIcon("icons/config.jpg"))

        self.restart_action = self.menu.addAction("Restart")
        self.restart_action.setVisible(False)
        self.restart_action.triggered.connect(self.restart)
        self.restart_action.setIcon(QtGui.QIcon("icons/restart.png"))

        self.start_action = self.menu.addAction("Start")
        self.start_action.triggered.connect(self.restart)
        self.start_action.setIcon(QtGui.QIcon("icons/play.png"))

        self.stop_action = self.menu.addAction("Stop")
        self.stop_action.setVisible(False)
        self.stop_action.triggered.connect(self.stop)
        self.stop_action.setIcon(QtGui.QIcon("icons/stop.png"))

        self.exit_action = self.menu.addAction("Exit")
        self.exit_action.triggered.connect(lambda: sys.exit())
        self.exit_action.setIcon(QtGui.QIcon("icons/exit.png"))
        self.setContextMenu(self.menu)

    def _update_ui(self):
        self.restart_action.setVisible(False)
        self.stop_action.setVisible(False)
        self.start_action.setVisible(False)

        if self.state is ServiceState.Started:
            self.restart_action.setVisible(True)
            self.stop_action.setVisible(True)
        elif self.state is ServiceState.Stopped:
            self.start_action.setVisible(True)

    def stop(self, show_message=True):
        if self.state is ServiceState.Stopped:
            pass

        self.service.stop()
        self.state = ServiceState.Stopped
        if show_message:
            self.showMessage('NDU Gate', 'Service stopped')
        self._update_ui()

    def start(self):
        if self.state is ServiceState.Started:
            pass

        if self.config_file is not None:
            self.service.start(self.config_file)

        self.state = ServiceState.Started
        self.showMessage('NDU Gate', 'Service started')

        self._update_ui()

    def restart(self):
        self.stop(False)
        self.start()

    def on_tray_icon_activated(self, reason):
        # if reason == self.DoubleClick:
        pass

    def set_config(self):
        self.config_file, _ = QFileDialog.getOpenFileName(None, 'Choose config file', 'C:\\',
                                                          "Config File (*.yml *.yaml)")
        self.restart()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()

    tray_icon = NDUGateTrayApplication(QtGui.QIcon("icons/icon.png"), w)
    tray_icon.show()
    # tray_icon.showMessage('VFX Pipeline', 'Hello "Name of logged in ID')
    code = app.exec_()
    sys.exit(code)


if __name__ == '__main__':
    main()
