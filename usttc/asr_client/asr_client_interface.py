from abc import ABC, abstractmethod
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.stream.stream import Stream


class AsrClientInterface(ABC):

    @abstractmethod
    def recognize(self, config: Config, audio: AudioFile):
        pass

    @abstractmethod
    def stream(self, stream: Stream, config: Config):
        pass
