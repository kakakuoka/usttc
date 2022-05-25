from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.asr_client.asr_provider import AsrProvider
import requests
import time


class AssemblyAiClient(AsrClient):
    provider = AsrProvider.ASSEMBLY_AI

    def __init__(self, token):
        self.token = token

    def recognize(self, audio: AudioFile, config: Config = Config()):

        def read_file(filename, chunk_size=5242880):
            with open(filename, 'rb') as _file:
                while True:
                    data = _file.read(chunk_size)
                    if not data:
                        break
                    yield data

        headers = {'authorization': self.token}
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=headers,
                                 data=read_file(audio.file))
        audio_url = response.json()["upload_url"]
        endpoint = "https://api.assemblyai.com/v2/transcript"
        dual_channel = config.separate_speaker_per_channel and (audio.channels == 2)
        json = {
            "audio_url": audio_url,
            "speaker_labels": (config.diarization is not None),
            "dual_channel": dual_channel,
            "language_code": config.language[:2]
        }

        response = requests.post(endpoint, json=json, headers=headers)

        _id = response.json()["id"]
        while True:
            time.sleep(5)
            polling_response = requests.get("https://api.assemblyai.com/v2/transcript/" + _id, headers=headers)
            r = polling_response.json()
            if r['status'] == 'completed':
                transcript = r["text"]
                words = []
                for w in r["words"]:
                    if dual_channel:
                        speaker = w.get("channel")
                    else:
                        speaker = w.get("speaker")
                    words.append(
                        Word(text=w["text"], confidence=w["confidence"], start=w["start"], end=w["end"],
                             speaker=speaker)
                    )
                return RecognizeResult(transcript=transcript, words=words)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        return AssemblyAiClient(token=key)
