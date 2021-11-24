from abc import ABC, abstractmethod
from uni_transcribe.messages import *
from uni_transcribe.stream.stream import Stream


class AsrClient(ABC):

    @abstractmethod
    def recognize(self, config: Config, audio: Audio):
        pass

    @abstractmethod
    def stream(self, stream: Stream, config: Config):
        pass

    @staticmethod
    @abstractmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def from_key(key: str, *args, **kwargs):
        pass
