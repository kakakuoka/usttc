from asr_bridge.asr_client.asr_client import AsrClient
from asr_bridge.messages import *
from voicegain_speech import ApiClient
from voicegain_speech import Configuration
from voicegain_speech import TranscribeApi


class VoicegainClient(AsrClient):
    def __init__(self, api_client):
        self.api_client = api_client
        self.transcribe_api = TranscribeApi(api_client)

    def recognize(self, config: Config, audio: Audio):
        audio_base64 = audio.base64_content

        response = self.transcribe_api.asr_transcribe_post(
            sync_transcription_request={
                "audio": {
                    "source": {
                        "inline": {
                            "data": audio_base64
                        }
                    },
                    "rate": config.sample_rate
                }
            }
        )
        alternatives = []
        if response.result:
            for alternative in response.result.alternatives:
                alternatives.append(Alternative(transcript=alternative.utterance,
                                                confidence=alternative.confidence))
        result = Result(alternatives)
        return result

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        with open(filename) as f:
            key = f.read().strip()
            return VoicegainClient.from_key(key, *args, **kwargs)

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        configuration = Configuration()
        configuration.access_token = key
        api_client = ApiClient(configuration=configuration)
        return VoicegainClient(api_client)
