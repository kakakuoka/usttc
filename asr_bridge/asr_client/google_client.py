from asr_bridge.asr_client.asr_client import AsrClient
from asr_bridge.messages import *
from google.cloud import speech


class GoogleClient(AsrClient):
    def __init__(self, client):
        self.client = client

    def recognize(self, config: Config, audio: Audio):
        response = self.client.recognize(
            config=self._generate_config_message(config),
            audio=self._generate_audio_message(audio)
        )
        results = response.results
        first_result = results[0]
        alternatives = []
        for alternative in first_result.alternatives:
            alternatives.append(Alternative(alternative.transcript, alternative.confidence))
        return Result(alternatives=alternatives)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        client = speech.SpeechClient.from_service_account_file(filename)
        return GoogleClient(client)

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        raise NotImplemented("Google ASR: Use key file authentication")

    @staticmethod
    def _generate_audio_message(audio):
        recog_audio = speech.RecognitionAudio()
        if audio.uri:
            recog_audio.uri = audio.uri
        elif audio.byte_array_content:
            recog_audio.content = audio.byte_array_content
        return recog_audio

    @staticmethod
    def _generate_config_message(config):
        recog_config = speech.RecognitionConfig(
            encoding=config.encoding,
            sample_rate_hertz=config.sample_rate,
            language_code=config.language
        )
        return recog_config
