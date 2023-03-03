from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile, AudioFormat
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.exceptions.exceptions import ConfigurationException, AudioException
from usttc.asr_client.asr_provider import AsrProvider
import azure.cognitiveservices.speech as speechsdk
import json
import time
import logging
import threading


class AzureClient(AsrClient):
    provider = AsrProvider.MICROSOFT_AZURE

    def __init__(self, key, region):
        self.key = key
        self.region = region
        self.speech_config_map = dict()
        self.lock = threading.Lock()

    def get_speech_config(self, lang):
        with self.lock:
            if lang not in self.speech_config_map:
                speech_config = speechsdk.SpeechConfig(subscription=self.key,
                                                       region=self.region,
                                                       speech_recognition_language=lang)
                speech_config.request_word_level_timestamps()
                self.speech_config_map[lang] = speech_config
                logging.info("Generate Speech config for lang {}".format(lang))
            return self.speech_config_map[lang]

    def recognize(self, audio: AudioFile, config: Config = Config()):

        if config.diarization:
            raise ConfigurationException("Azure python SDK does not support diarization. "
                                         "Will switch to batch transcription API later on")
        if config.separate_speaker_per_channel and audio.channels > 1:
            raise ConfigurationException("Azure python SDK does not support multi-channel audio. "
                                         "Will switch to batch transcription API later on")

        speech_config = self.get_speech_config(config.language)

        convert_audio = False
        if audio.codec != AudioFormat.LINEAR16:
            audio = audio.convert()
            convert_audio = True

        audio_input = speechsdk.AudioConfig(filename=audio.file)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        done = {}
        words = []
        transcripts = []

        def stop_cb(evt):
            speech_recognizer.stop_continuous_recognition()
            done["done"] = True

        def recognized_cb(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                result = evt.result
                transcripts.append(result.text)
                n_best = json.loads(result.json).get("NBest")
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

        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        # Start continuous speech recognition
        speech_recognizer.start_continuous_recognition()
        while not done:
            time.sleep(.5)

        speech_recognizer.stop_continuous_recognition()
        speech_recognizer.canceled.disconnect_all()
        speech_recognizer.recognized.disconnect_all()
        speech_recognizer.session_stopped.disconnect_all()
        del speech_recognizer

        if convert_audio:
            audio.delete()
        return RecognizeResult(transcript=" ".join(transcripts), words=words)

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
