from uni_transcribe.asr_client.asr_client_interface import AsrClientInterface
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile
from uni_transcribe.stream.stream import Stream


class MultiAsrClient(AsrClientInterface):

    def __init__(self, asr_clients):
        """
        :param asr_clients: List of asr_client
        """
        self.asr_clients = asr_clients

    def recognize(self, config: Config, audio: AudioFile):
        results_map = dict()
        for asr_client in self.asr_clients:
            result = asr_client.recognize(config, audio)
            results_map[asr_client.provider] = result
        return results_map

    def stream(self, stream: Stream, config: Config):
        pass
