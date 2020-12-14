import enum
import sys
from os import path

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog

import logging

from ndu_gate_camera import NDUCameraService
from ndu_gate_camera.camera.ndu_logger import NDULoggerHandler
from ndu_gate_camera.camera.result_handlers.result_handler_file import ResultHandlerFile
from ndu_gate_camera.camera.result_handlers.result_handler_socket import ResultHandlerSocket
from ndu_gate_camera.utility.constants import DEFAULT_HANDLER_SETTINGS
from yaml import safe_load
from tendo import singleton
from tendo.singleton import SingleInstanceException

class ServiceState(enum.Enum):
    Started = 1
    Stopped = 2


class NDUGateServiceWrapper:
    def __init__(self):
        self.ndu_gate_config = {}
        self.instances = []

    def stop(self):
        if len(self.instances) > 0:
            for instance in self.instances:
                instance.exit_signal()
                instance.join()

            self.instances = []
            print("All instances stopped!")

    def start(self, ndu_gate_config_file: str):
        self.ndu_gate_config = {}
        self.instances = []

        if not path.isfile(ndu_gate_config_file):
            print('config parameter is not a file : ', ndu_gate_config_file)
            sys.exit(2)

        print("Using config file : {}".format(ndu_gate_config_file))
        with open(ndu_gate_config_file, encoding="utf-8") as general_config:
            self.ndu_gate_config = safe_load(general_config)

        ndu_gate_config_dir = path.dirname(path.abspath(ndu_gate_config_file)) + path.sep

        logging_config_file = ndu_gate_config_dir + "logs.conf"
        try:
            import platform
            if platform.system() == "Darwin":
                ndu_gate_config_dir + "logs_macosx.conf"
            # logging.config.fileConfig(logging_config_file, disable_existing_loggers=False)
        except Exception as e:
            print(e)
            NDULoggerHandler.set_default_handler()

        global log
        log = logging.getLogger('service')
        log.info("NDU-Gate logging config file: %s", logging_config_file)
        log.info("NDU-Gate logging service level: %s", log.level)

        result_hand_conf = self.ndu_gate_config.get("result_handler", None)
        if result_hand_conf is None:
            result_hand_conf = DEFAULT_HANDLER_SETTINGS

        if str(result_hand_conf.get("type", "SOCKET")) == str("SOCKET"):
            result_handler = ResultHandlerSocket(result_hand_conf.get("socket", {}),
                                                 result_hand_conf.get("device", None))
        else:
            result_handler = ResultHandlerFile(result_hand_conf.get("file_path", None))

        if self.ndu_gate_config.get("instances", None) is not None > 0:
            for instance in self.ndu_gate_config.get("instances", []):
                camera_service = NDUCameraService(instance=instance, config_dir=ndu_gate_config_dir,
                                                  handler=result_handler, is_main_thread=False)
                camera_service.start()
                self.instances.append(camera_service)
                log.info("NDU-Gate an instance started")
            log.info("NDU-Gate all instances are started")
        else:
            log.error("NDUCameraService no source found!")


class NDUGateTrayApplication(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'NDU Gate Camera Service - 0.1.8')

        self._init_ui(parent)

        self.activated.connect(self.on_tray_icon_activated)

        self.service = NDUGateServiceWrapper()
        self.config_file = None
        self.state = ServiceState.Stopped

    def _init_ui(self, parent):
        self.menu = QtWidgets.QMenu(parent)

        self.config_action = self.menu.addAction("Set Config")
        self.config_action.triggered.connect(self.set_config)
        self.config_action.setIcon(QtGui.QIcon(icon_path("config.jpg")))

        self.restart_action = self.menu.addAction("Restart")
        self.restart_action.setVisible(False)
        self.restart_action.triggered.connect(self.restart)
        self.restart_action.setIcon(QtGui.QIcon(icon_path("restart.png")))

        self.start_action = self.menu.addAction("Start")
        self.start_action.triggered.connect(self.restart)
        self.start_action.setIcon(QtGui.QIcon(icon_path("play.png")))

        self.stop_action = self.menu.addAction("Stop")
        self.stop_action.setVisible(False)
        self.stop_action.triggered.connect(self.stop)
        self.stop_action.setIcon(QtGui.QIcon(icon_path("stop.png")))

        self.exit_action = self.menu.addAction("Exit")
        self.exit_action.triggered.connect(lambda: sys.exit())
        self.exit_action.setIcon(QtGui.QIcon(icon_path("exit.png")))
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

        if self.config_file:
            self.config_action.setToolTip(self.config_file)
        else:
            self.config_action.setToolTip("Config file is not selected")

    def stop(self, show_message=True):
        if self.state is ServiceState.Stopped:
            return

        self.service.stop()
        self.state = ServiceState.Stopped
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

        self.state = ServiceState.Started
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
