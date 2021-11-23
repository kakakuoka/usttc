from asr_bridge.asr_client.asr_client import AsrClient
from asr_bridge.messages import *
from asr_bridge.exceptions.exceptions import ConfigurationException, AudioException
from asr_bridge.utils import generate_random_str


class WatsonClient(AsrClient):
    def __init__(self):
        pass

    def recognize(self, config: Config, audio: Audio):
        pass

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        pass
