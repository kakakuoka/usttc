from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.messages import *
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
from uni_transcribe.utils import generate_random_str


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
