import sys
from os import path

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from tendo import singleton
from tendo.singleton import SingleInstanceException
from services import NDUGateServiceWrapper, ServiceState


class NDUGateTrayApplication(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'NDU Gate Camera Service - 0.1.8')

        self._init_ui(parent)

        self.activated.connect(self.on_tray_icon_activated)

        self.service = NDUGateServiceWrapper()
        self.config_file = None

    def _init_ui(self, parent):
        self.menu = QtWidgets.QMenu(parent)

        self.menu.addSeparator()

        #region NDU-Gate Camera Service
        self.nduGateMenu = self.menu.addMenu("NDU-Gate Camera Service")
        self.nduGateMenu.setIcon(QtGui.QIcon(icon_path("ndu_gate_icon.png")))

        self.ndu_gate_config_action = self.nduGateMenu.addAction("Set Config")
        self.ndu_gate_config_action.triggered.connect(self.set_config)
        self.ndu_gate_config_action.setIcon(QtGui.QIcon(icon_path("config.jpg")))

        self.ndu_gate_restart_action = self.nduGateMenu.addAction("Restart")
        self.ndu_gate_restart_action.setVisible(False)
        self.ndu_gate_restart_action.triggered.connect(self.restart)
        self.ndu_gate_restart_action.setIcon(QtGui.QIcon(icon_path("restart.png")))

        self.ndu_gate_start_action = self.nduGateMenu.addAction("Start")
        self.ndu_gate_start_action.triggered.connect(self.restart)
        self.ndu_gate_start_action.setIcon(QtGui.QIcon(icon_path("play.png")))

        self.ndu_gate_stop_action = self.nduGateMenu.addAction("Stop")
        self.ndu_gate_stop_action.setVisible(False)
        self.ndu_gate_stop_action.triggered.connect(self.stop)
        self.ndu_gate_stop_action.setIcon(QtGui.QIcon(icon_path("stop.png")))
        #endregion

        self.menu.addSeparator()

        #region NDU Gateway Service Menu
        self.tbGateMenu = self.menu.addMenu("NDU Gateway Service")
        self.tbGateMenu.setIcon(QtGui.QIcon(icon_path("tb_gate_icon.png")))

        self.tb_gate_config_action = self.tbGateMenu.addAction("Set Config")
        self.tb_gate_config_action.triggered.connect(self.set_config)
        self.tb_gate_config_action.setIcon(QtGui.QIcon(icon_path("config.jpg")))

        self.tb_gate_restart_action = self.tbGateMenu.addAction("Restart")
        self.tb_gate_restart_action.setVisible(False)
        self.tb_gate_restart_action.triggered.connect(self.restart)
        self.tb_gate_restart_action.setIcon(QtGui.QIcon(icon_path("restart.png")))

        self.tb_gate_start_action = self.tbGateMenu.addAction("Start")
        self.tb_gate_start_action.triggered.connect(self.restart)
        self.tb_gate_start_action.setIcon(QtGui.QIcon(icon_path("play.png")))

        self.tb_gate_stop_action = self.tbGateMenu.addAction("Stop")
        self.tb_gate_stop_action.setVisible(False)
        self.tb_gate_stop_action.triggered.connect(self.stop)
        self.tb_gate_stop_action.setIcon(QtGui.QIcon(icon_path("stop.png")))
        #endregion

        self.menu.addSeparator()

        self.exit_action = self.menu.addAction("Exit")
        self.exit_action.triggered.connect(lambda: sys.exit())
        self.exit_action.setIcon(QtGui.QIcon(icon_path("exit.png")))
        self.setContextMenu(self.menu)

    def _update_ui(self):
        self.ndu_gate_restart_action.setVisible(False)
        self.ndu_gate_stop_action.setVisible(False)
        self.ndu_gate_start_action.setVisible(False)

        if self.service.state is ServiceState.Started:
            self.ndu_gate_restart_action.setVisible(True)
            self.ndu_gate_stop_action.setVisible(True)
        elif self.state is ServiceState.Stopped:
            self.ndu_gate_start_action.setVisible(True)

        if self.config_file:
            self.ndu_gate_config_action.setToolTip(self.config_file)
        else:
            self.ndu_gate_config_action.setToolTip("Config file is not selected")

    def stop(self, show_message=True):
        if self.state is ServiceState.Stopped:
            return

        self.service.stop()
        self.service.state = ServiceState.Stopped
        if show_message:
            self.showMessage('NDU Gate', 'Service stopped')
        self._update_ui()

    def start(self):
        if self.state is ServiceState.Started:
            return

        if self.config_file is not None:
            if not path.isfile(self.config_file):
                self.show_message("Selected path is not file!", is_error=True)
                return
        else:
            self.show_message("Config file is not selected", is_error=True)
            return

        if self.config_file is not None:
            self.service.start(self.config_file)

        self.service.state = ServiceState.Started
        self.showMessage('NDU Gate', 'Service started')

        self._update_ui()

    def restart(self):
        self.stop(False)
        self.start()

    def on_tray_icon_activated(self, reason):
        # if reason == self.DoubleClick:
        return

    def show_message(self, message: str, is_error=False):
        self.showMessage('NDU Gate', message)
        message_type: str = is_error if "ERROR" else "DEBUG"
        print("{} - {}".format(message_type, message))

    def set_config(self):
        selected_file, _ = QFileDialog.getOpenFileName(
            None, 'Select config', 'C:\\', "Config File (*.yml *.yaml)")
        if selected_file:
            self.config_file = selected_file


def icon_path(icon_name):
    if hasattr(sys, '_MEIPASS'):
        return path.join(sys._MEIPASS, 'icons', icon_name)
    return path.join(path.abspath("."), 'icons', icon_name)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    w = QtWidgets.QWidget()

    ndu_gate_tray_app = NDUGateTrayApplication(QtGui.QIcon(icon_path("app_icon.png")), w)
    ndu_gate_tray_app.show()

    try:
        singleton.SingleInstance()
    except SingleInstanceException as e:
        ndu_gate_tray_app.setToolTip("App already running...")
        sys.exit(-1)

    code = app.exec_()
    sys.exit(code)


if __name__ == '__main__':
    main()
