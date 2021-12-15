from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile, AudioFormat
from uni_transcribe.result.recognize_result import RecognizeResult
from uni_transcribe.result.word import Word
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
import azure.cognitiveservices.speech as speechsdk
import json
import logging


class AzureClient(AsrClient):
    def __init__(self, key, region):
        self.key = key
        self.region = region

    def recognize(self, config: Config, audio: AudioFile):

        if config.diarization:
            raise ConfigurationException("Azure python SDK does not support diarization. "
                                         "Will switch to batch transcription API later on")
        if config.separate_speaker_per_channel and audio.channels > 1:
            raise ConfigurationException("Azure python SDK does not support multi-channel audio. "
                                         "Will switch to batch transcription API later on")

        speech_config = speechsdk.SpeechConfig(subscription=self.key,
                                               region=self.region)
        speech_config.request_word_level_timestamps()

        convert_audio = False
        if audio.codec != AudioFormat.LINEAR16:
            audio = audio.convert()
            convert_audio = True

        audio_input = speechsdk.AudioConfig(filename=audio.file)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        result = speech_recognizer.recognize_once_async().get()
        transcript = result.text
        n_best = json.loads(result.json).get("NBest")
        words = []
        if n_best:
            top_1 = n_best[0]
            confidence = top_1["Confidence"]
            for w in top_1["Words"]:
                words.append(
                    Word(
                        text=w["Word"], confidence=confidence,
                        start=w["Offset"] / 10000,
                        duration=w["Duration"] / 10000
                    )
                )

        if convert_audio:
            audio.delete()
        return RecognizeResult(transcript=transcript, words=words)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Azure ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        logging.info("Azure integration is Alpha version")
        region = kwargs.get("region")
        if not region:
            raise ConfigurationException("Azure ASR: Specify region arg")
        return AzureClient(key, region)
