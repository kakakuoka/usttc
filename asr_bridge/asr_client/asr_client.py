from abc import ABC, abstractmethod
from asr_bridge.messages import *


class AsrClient(ABC):

    @abstractmethod
    def recognize(self, config: Config, audio: Audio):
        pass

    @abstractmethod
    def stream(self):
        pass

    @staticmethod
    @abstractmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def from_key(key: str, *args, **kwargs):
        pass
