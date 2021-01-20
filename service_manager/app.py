import functools
import sys
from os import path

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog
from tendo import singleton
from tendo.singleton import SingleInstanceException

from service_manager.services.ndu_gate_service_wrapper import NDUGateServiceWrapper
from service_manager.services.service_wrapper import ServiceState
from service_manager.services.tb_gate_service_wrapper import TBGatewayServiceWrapper


class NDUGateTrayApplication(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'NDU Gate Service Manager - 0.2')

        self.service_registry = {
            'ndu-gate': {
                'service': NDUGateServiceWrapper(),
                'name': 'NDU-Gate Camera Service',
                'icon': 'ndu_gate_icon.png'
            },
            'tb-gate': {
                'service': TBGatewayServiceWrapper(),
                'name': 'Thingsboard Gateway Service',
                'icon': 'tb_gate_icon.png'
            }
        }

        self._init_ui(parent)

        self.activated.connect(self.on_tray_icon_activated)
        self.config_file = None

    def _init_ui(self, parent):
        self.menu = QtWidgets.QMenu(parent)

        for instance_name in self.service_registry:
            self.menu.addSeparator()
            name = self.service_registry[instance_name]['name']
            ndu_gate_menu = self.menu.addMenu(name)
            ndu_gate_menu.setIcon(QtGui.QIcon(icon_path(self.service_registry[instance_name]['icon'])))

            ndu_gate_config_action = ndu_gate_menu.addAction("Set Config")
            ndu_gate_config_action.triggered.connect(functools.partial(self.set_config, instance_name))
            ndu_gate_config_action.setIcon(QtGui.QIcon(icon_path("config.jpg")))

            ndu_gate_restart_action = ndu_gate_menu.addAction("Restart")
            ndu_gate_restart_action.setVisible(False)
            ndu_gate_restart_action.triggered.connect(functools.partial(self.restart, instance_name))
            ndu_gate_restart_action.setIcon(QtGui.QIcon(icon_path("restart.png")))

            ndu_gate_start_action = ndu_gate_menu.addAction("Start")
            ndu_gate_start_action.triggered.connect(functools.partial(self.restart, instance_name))
            ndu_gate_start_action.setIcon(QtGui.QIcon(icon_path("play.png")))

            ndu_gate_stop_action = ndu_gate_menu.addAction("Stop")
            ndu_gate_stop_action.setVisible(False)
            ndu_gate_stop_action.triggered.connect(functools.partial(self.stop, instance_name))
            ndu_gate_stop_action.setIcon(QtGui.QIcon(icon_path("stop.png")))

            self.service_registry[instance_name]['menu'] = ndu_gate_menu

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

    def stop(self, instance_name, show_message=True):
        if not instance_name or self.service_registry.get(instance_name, None) is None:
            return

        if self.service_registry[instance_name]['service'].state is ServiceState.Stopped:
            return

        self.service_registry[instance_name]['service'].stop()
        self.service_registry[instance_name]['service'].state = ServiceState.Stopped
        if show_message:
            self.showMessage('NDU Gate', 'Service stopped')
        self._update_ui()

    def start(self, instance_name):
        if not instance_name or self.service_registry.get(instance_name, None) is None:
            return

        if self.service_registry[instance_name]['service'].state is ServiceState.Started:
            return

        if self.config_file is not None:
            if not path.isfile(self.config_file):
                self.show_message("Selected path is not file!", is_error=True)
                return
        else:
            self.show_message("Config file is not selected", is_error=True)
            return

        if self.config_file is not None:
            self.service_registry[instance_name]['service'].start(self.config_file)

        self.service_registry[instance_name]['service'].state = ServiceState.Started
        self.showMessage('NDU Gate', 'Service started')

        self._update_ui()

    def restart(self, instance_name):
        if not instance_name or self.service_registry.get(instance_name, None) is None:
            return

        self.stop(instance_name, show_message=False)
        self.start(instance_name)

    def on_tray_icon_activated(self, reason):
        # if reason == self.DoubleClick:
        return

    def show_message(self, message: str, is_error=False):
        self.showMessage('NDU Gate', message)
        message_type: str = is_error if "ERROR" else "DEBUG"
        print("{} - {}".format(message_type, message))

    def set_config(self, instance_name):
        if not instance_name or self.service_registry.get(instance_name, None) is None:
            return

        selected_file, _ = QFileDialog.getOpenFileName(
            None, 'Select config', 'C:\\', "Config File (*.yml *.yaml)")
        if selected_file:
            self.service_registry[instance_name]['service'].set_config(selected_file)


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
        print(e)
        sys.exit(-1)

    code = app.exec_()
    sys.exit(code)


if __name__ == '__main__':
    main()
