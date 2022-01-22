from usttc.asr_client.asr_client_interface import AsrClientInterface
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.stream.stream import Stream


class MultiAsrClient(AsrClientInterface):

    def __init__(self, asr_clients):
        """
        :param asr_clients: List of asr_client
        """
        self.asr_clients = asr_clients

    def recognize(self, audio: AudioFile, config: Config = Config()):
        results_map = dict()
        for asr_client in self.asr_clients:
            result = asr_client.recognize(audio, config)
            results_map[asr_client.provider] = result
        return results_map

    def stream(self, stream: Stream, config: Config):
        pass
