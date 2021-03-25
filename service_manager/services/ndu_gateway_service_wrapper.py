import os

from ndu_gateway import TBGatewayService
from yaml import safe_load

from service_manager.services.service_wrapper import ServiceWrapper, ServiceState


class NDUGatewayServiceWrapper(ServiceWrapper):
    """

    """
    def __init__(self, config_file: str = None):
        super().__init__(config_file)
        self.ndu_gateway_config = {}
        self.instance: TBGatewayService = None

    def set_config(self, config_file):
        self.config_file = config_file
        self.ndu_gateway_config = {}
        self.instance = None

        if not os.path.isfile(config_file):
            print('NDUGatewayServiceWrapper config parameter is not a file : ', config_file)
            exit(2)

        print("NDUGatewayServiceWrapper using config file : {}".format(config_file))
        with open(config_file, encoding="utf-8") as general_config:
            self.ndu_gateway_config = safe_load(general_config)

    def start(self):
        self.state = ServiceState.Started
        try:
            self.instance = TBGatewayService(config_file=self.config_file, is_main_thread=False)
        except Exception as ex:
            self.state = ServiceState.Stopped
            print(ex)

    def stop(self):
        self.state = ServiceState.Stopped
        self.instance.stop_gateway()
