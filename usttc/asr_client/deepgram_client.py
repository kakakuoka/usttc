from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.exceptions.exceptions import ConfigurationException, AudioException
from usttc.asr_client.asr_provider import AsrProvider
from deepgram import Deepgram
import asyncio


class DeepgramClient(AsrClient):
    provider = AsrProvider.DEEPGRAM

    def __init__(self, client):
        self.client = client

    def recognize(self, audio: AudioFile, config: Config = Config()):
        response = asyncio.run(self.async_recognize(config, audio))
        word_list = []
        results = response["results"]
        channels = results.get("channels")
        if channels:
            for (M, channel) in enumerate(channels):
                alternatives = channel["alternatives"]
                words = alternatives[0]["words"]
                for word in words:
                    if len(channels) > 1:
                        speaker = M
                    else:
                        speaker = word.get("speaker")
                    word_list.append(
                        Word(
                            text=word["punctuated_word"], confidence=word["confidence"],
                            start=word["start"] * 1000,
                            end=word["end"] * 1000,
                            speaker=speaker
                        )
                    )

        return RecognizeResult(words=word_list)

    async def async_recognize(self, config: Config, audio: AudioFile):
        with open(audio.file, 'rb') as audio_file:
            # Replace mimetype as appropriate
            source = {'buffer': audio_file, 'mimetype': 'audio/*'}
            response = await self.client.transcription.prerecorded(
                source,
                {
                    'punctuate': True,
                    "diarize": (config.diarization is not None),
                    "multichannel": config.separate_speaker_per_channel and (audio.channels > 1),
                    'language': config.language
                }
            )
            return response

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Deepgram ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        client = Deepgram(key)
        return DeepgramClient(client)
