from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.messages import *
from uni_transcribe.audio_transcoder.audio_file import AudioFormat
from uni_transcribe.exceptions.exceptions import AudioException
from voicegain_speech import ApiClient
from voicegain_speech import Configuration
from voicegain_speech import TranscribeApi, DataApi
import time


OFFLINE_FILE_SIZE_LIMIT = 150 * 1024 * 1024


class VoicegainClient(AsrClient):
    def __init__(self, api_client):
        self.api_client = api_client
        self.transcribe_api = TranscribeApi(api_client)
        self.data_api = DataApi(api_client)

    def recognize(self, config: Config, audio: Audio):
        if audio.duration < 30 and audio.channels == 1 and audio.codec == AudioFormat.LINEAR16:
            # use sync transcribe for short audio
            return self._sync_transcribe(config, audio)
        elif audio.file_size > OFFLINE_FILE_SIZE_LIMIT:
            raise AudioException("Audio file size is larger than 150MB. Voicegain does not support that")
        else:
            data_object = self.data_api.data_file_post(file=audio.file)
            object_id = data_object.object_id
            audio_source = {
                "dataStore": {
                    "uuid": object_id
                }
            }
            result = self._async_transcribe(config, audio, audio_source)
            self.data_api.data_delete(uuid=object_id)
            return result

    def stream(self):
        pass

    def _sync_transcribe(self, config: Config, audio: Audio):
        audio_base64 = audio.base64_content
        response = self.transcribe_api.asr_transcribe_post(
            sync_transcription_request={
                "audio": {
                    "source": {
                        "inline": {
                            "data": audio_base64
                        }
                    }
                }
            }
        )
        if response.result:
            for alternative in response.result.alternatives:
                return Result(
                    transcript=alternative.utterance,
                    confidence=alternative.confidence
                )
        return Result("", 1)

    def _async_transcribe(self, config: Config, audio: Audio, audio_source):
        async_transcription_request = {
            "sessions": [
                {
                    "asyncMode": "OFF-LINE",
                    "poll": {
                        "afterlife": 60000,
                        "persist": 0
                    }
                }
            ],
            "audio": {
                "source": audio_source
            }
        }

        async_transcribe_init_response = self.transcribe_api.asr_transcribe_async_post(
            async_transcription_request=async_transcription_request
        )

        async_response_session = async_transcribe_init_response.sessions[0]
        session_id = async_response_session.session_id

        while True:
            time.sleep(5)
            poll_response = self.transcribe_api.asr_transcribe_async_get(
                session_id=session_id,
                full=True
            )
            poll_response_result = poll_response.result

            if poll_response_result.final:
                # get to final
                result_transcript = poll_response_result.transcript
                result = Result(transcript=result_transcript, confidence=1)
                return result
            else:
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
