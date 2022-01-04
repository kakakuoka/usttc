from usttc.asr_client.asr_client_interface import AsrClientInterface
from abc import abstractmethod


class AsrClient(AsrClientInterface):

    @staticmethod
    @abstractmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def from_key(key: str, *args, **kwargs):
        pass
