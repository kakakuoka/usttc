from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.stream.stream import Stream
from usttc.asr_client.asr_provider import AsrProvider


class RivaClient(AsrClient):
    provider = AsrProvider.RIVA

    def __init__(self):
        pass

    def recognize(self, audio: AudioFile, config: Config = Config()):
        pass

    def stream(self, stream: Stream, config: Config):
        # don't need to support now
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        pass
