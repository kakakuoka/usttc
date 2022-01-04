from abc import ABC, abstractmethod
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile
from uni_transcribe.stream.stream import Stream


class AsrClientInterface(ABC):

    @abstractmethod
    def recognize(self, config: Config, audio: AudioFile):
        pass

    @abstractmethod
    def stream(self, stream: Stream, config: Config):
        pass
