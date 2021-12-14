from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile
from uni_transcribe.result.recognize_result import RecognizeResult
from uni_transcribe.result.word import Word
import requests
import time


class AssemblyAiClient(AsrClient):
    def __init__(self, token):
        self.token = token

    def recognize(self, config: Config, audio: AudioFile):

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
            "dual_channel": dual_channel
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
