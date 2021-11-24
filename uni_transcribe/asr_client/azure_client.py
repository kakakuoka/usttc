from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.messages import *
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
import azure.cognitiveservices.speech as speechsdk


class AzureClient(AsrClient):
    def __init__(self, key, region):
        self.key = key
        self.region = region

    def recognize(self, config: Config, audio: Audio):

        speech_config = speechsdk.SpeechConfig(subscription=self.key,
                                               region=self.region)
        audio_input = speechsdk.AudioConfig(filename=audio.file)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        result = speech_recognizer.recognize_once_async().get()
        return Result(transcript=result.text, confidence=1)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Azure ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        region = kwargs.get("region")
        if not region:
            raise ConfigurationException("Azure ASR: Specify region arg")
        return AzureClient(key, region)
