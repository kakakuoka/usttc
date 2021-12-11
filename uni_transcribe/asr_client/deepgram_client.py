from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
from uni_transcribe.utils import generate_random_str


class DeepgramClient(AsrClient):
    def __init__(self):
        pass

    def recognize(self, config: Config, audio: AudioFile):
        pass

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Deepgram ASR: Not support")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        raise ConfigurationException("Deepgram ASR: Not support")
