import logging
import os

from ndu_gate_camera import NDUCameraService
from ndu_gate_camera.camera.ndu_logger import NDULoggerHandler
from ndu_gate_camera.camera.result_handlers.result_handler_file import ResultHandlerFile
from ndu_gate_camera.camera.result_handlers.result_handler_socket import ResultHandlerSocket
from ndu_gate_camera.utility.constants import DEFAULT_HANDLER_SETTINGS
from yaml import safe_load

from service_manager.services.service_wrapper import ServiceState, ServiceWrapper


class NDUGateServiceWrapper(ServiceWrapper):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)
        self.ndu_gate_config = {}
        self.instances = []

    def set_config(self, config_file={}):
        self.config_file = config_file
        self.ndu_gate_config = {}
        self.instances = []

        if not os.path.isfile(config_file):
            print('config parameter is not a file : ', config_file)
            exit(2)

        print("Using config file : {}".format(config_file))
        with open(config_file, encoding="utf-8") as general_config:
            self.ndu_gate_config = safe_load(general_config)

    def start(self):
        ndu_gate_config_dir = os.path.dirname(os.path.abspath(self.config_file)) + os.path.sep
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

        self.state = ServiceState.Started

    def stop(self):
        if len(self.instances) > 0:
            for instance in self.instances:
                instance.exit_signal()
                instance.join()

            self.instances = []
            print("All instances stopped!")
        self.state = ServiceState.Stopped
