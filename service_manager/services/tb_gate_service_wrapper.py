from service_manager.services.service_wrapper import ServiceWrapper, ServiceState


class TBGatewayServiceWrapper(ServiceWrapper):
    def __init__(self, config_file: str = None):
        super().__init__(config_file)
        self.ndu_gate_config = {}
        self.instances = []

    def set_config(self, config_file):
        self.config_file = config_file
        pass

    def start(self, config_file: str):
        self.state = ServiceState.Started
        pass

    def stop(self):
        self.state = ServiceState.Stopped
        pass
