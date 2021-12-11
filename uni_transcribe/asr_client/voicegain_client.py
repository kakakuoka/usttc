from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile
from uni_transcribe.result.recognize_result import RecognizeResult
from uni_transcribe.result.word import Word
from uni_transcribe.exceptions.exceptions import AudioException
from uni_transcribe.stream.stream import Stream
from voicegain_speech import ApiClient
from voicegain_speech import Configuration
from voicegain_speech import TranscribeApi, DataApi
import time
import asyncio
import websockets
import threading


OFFLINE_FILE_SIZE_LIMIT = 150 * 1024 * 1024


class VoicegainClient(AsrClient):
    def __init__(self, api_client):
        self.api_client = api_client
        self.transcribe_api = TranscribeApi(api_client)
        self.data_api = DataApi(api_client)

    def recognize(self, config: Config, audio: AudioFile):
        if audio.file_size > OFFLINE_FILE_SIZE_LIMIT:
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

    def stream(self, stream: Stream, config: Config):
        audio_ws_url, result_ws_url = self._start_async_web_socket_stream()
        result_ws_thread = threading.Thread(target=self._receive_result_thread, args=(result_ws_url, ))
        result_ws_thread.start()
        asyncio.run(self._stream_audio(stream, audio_ws_url))
        result_ws_thread.join()

    def _async_transcribe(self, config: Config, audio: AudioFile, audio_source):
        async_transcription_request = {
            "sessions": [
                {
                    "asyncMode": "OFF-LINE",
                    "poll": {
                        "afterlife": 60000,
                        "persist": 0
                    },
                    "content": {
                        "full": ["progress", "words", "transcript"]
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
                words = []
                if poll_response_result.words:
                    for word in poll_response_result.words:
                        words.append(Word(
                            text=word.utterance,
                            confidence=word.confidence,
                            start=word.start,
                            duration=word.duration,
                            speaker=word.spk
                        ))
                result = RecognizeResult(transcript=result_transcript, words=words)
                return result
            else:
                pass

    def _start_async_web_socket_stream(self):
        async_transcription_request = {
            "sessions": [
                {
                    "asyncMode": "REAL-TIME",
                    "websocket": {
                        "adHoc": True,
                        "useSTOMP": False,
                        "minimumDelay": 0
                    },
                    "content": {
                        "incremental": ['words'],
                        "full": []
                    }
                }
            ],
            "audio": {
                "source": {
                    "stream": {
                        "protocol": "WEBSOCKET"
                    }
                },
                "format": "L16",
                "channel": "mono",
                "rate": 16000
            }
        }
        async_transcribe_init_response = self.transcribe_api.asr_transcribe_async_post(
            async_transcription_request=async_transcription_request
        )
        audio_ws_url = async_transcribe_init_response.audio.stream.websocket_url
        result_ws_url = async_transcribe_init_response.sessions[0].websocket.url
        return audio_ws_url, result_ws_url

    @staticmethod
    async def _stream_audio(stream: Stream, audio_ws_url: str):
        async with websockets.connect(audio_ws_url,
                                      # we need to lower the buffer size - otherwise the sender will buffer for too long
                                      write_limit=480, compression=None) as websocket:
            try:
                for byte_buf in stream.generator():
                    await websocket.send(byte_buf)
                print("Waiting 5 seconds for processing to finish...", flush=True)
                time.sleep(5.0)
                print("done waiting", flush=True)
                await websocket.close()
            except Exception as e:
                print("Exception when sending audio via websocket: " + str(e))

    def _receive_result_thread(self, result_ws_url: str):
        try:
            asyncio.run(self._websocket_receive(result_ws_url))
        except Exception as e:
            print(e)

    @staticmethod
    async def _websocket_receive(result_ws_url: str):
        async with websockets.connect(result_ws_url,
                                      write_limit=480,
                                      # compression needs to be disabled otherwise will buffer for too long
                                      compression=None) as websocket:
            try:
                while True:
                    msg = await websocket.recv()
                    print(msg)
            except Exception as e:
                print(e)

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
