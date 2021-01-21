import enum
from abc import ABC, abstractmethod


class ServiceWrapper(ABC):

    def __init__(self):
        self.state = ServiceState.Stopped
        self.config_file = None

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def set_config(self, config_file):
        pass

    @abstractmethod
    def stop(self):
        pass

    def get_state(self):
        return self.state


class ServiceState(enum.Enum):
    Started = 1
    Stopped = 2
