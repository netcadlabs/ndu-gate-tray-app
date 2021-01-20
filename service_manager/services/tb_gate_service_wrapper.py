from service_manager.services.service_wrapper import ServiceWrapper, ServiceState


class TBGatewayServiceWrapper(ServiceWrapper):
    def start(self):
        self.state = ServiceState.Started
        pass

    def set_config(self, config={}):
        pass

    def stop(self):
        self.state = ServiceState.Stopped
        pass

    def __init__(self):
        super().__init__()
        self.ndu_gate_config = {}
        self.instances = []