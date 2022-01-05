from usttc.asr_client.asr_client_interface import AsrClientInterface
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.stream.stream import Stream
from usttc.exceptions.exceptions import ConfigurationException
from usttc.asr_client.multi_asr_client import MultiAsrClient


class EnsembleAsrClient(AsrClientInterface):

    def __init__(self, asr_clients):
        """
        :param asr_clients: List of asr_client
        """
        if len(asr_clients) < 3:
            raise ConfigurationException("Need at least 3 asr clients to ensemble")
        self.multi_asr_client = MultiAsrClient(asr_clients)

    def recognize(self, config: Config, audio: AudioFile):
        results_map = self.multi_asr_client.recognize(config, audio)
        # TODO
        return results_map

    def stream(self, stream: Stream, config: Config):
        pass
