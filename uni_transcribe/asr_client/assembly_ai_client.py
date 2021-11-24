from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.messages import *
import requests
import time
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
from uni_transcribe.utils import generate_random_str


class AssemblyAiClient(AsrClient):
    def __init__(self, token):
        self.token = token

    def recognize(self, config: Config, audio: Audio):

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
        json = {"audio_url": audio_url}

        response = requests.post(endpoint, json=json, headers=headers)

        _id = response.json()["id"]
        while True:
            time.sleep(5)
            polling_response = requests.get("https://api.assemblyai.com/v2/transcript/" + _id, headers=headers)
            if polling_response.json()['status'] == 'completed':
                transcript = polling_response.json()["text"]
                return Result(transcript=transcript, confidence=1)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        pass

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        return AssemblyAiClient(token=key)
