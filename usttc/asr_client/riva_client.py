from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile, AudioFormat
from usttc.stream.stream import Stream
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.asr_client.asr_provider import AsrProvider
from usttc.exceptions.exceptions import ConfigurationException
import riva.client


class RivaClient(AsrClient):
    provider = AsrProvider.RIVA

    def __init__(self, client):
        self.client = client

    def recognize(self, audio: AudioFile, config: Config = Config()):

        convert_audio = False
        # if (audio.channels > 1) and (not config.separate_speaker_per_channel):
        #     audio = audio.convert(to="wav", sample_rate=audio.sample_rate, to_mono=True)
        #     convert_audio = True
        # elif audio.codec != AudioFormat.LINEAR16:
        #     audio = audio.convert(to="wav", sample_rate=audio.sample_rate)
        #     convert_audio = True
        if (audio.channels > 1) or (audio.codec != AudioFormat.LINEAR16):
            audio = audio.convert(to="wav", sample_rate=audio.sample_rate, to_mono=True)
            convert_audio = True

        riva_config = riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            language_code=config.language,
            max_alternatives=1,
            enable_word_time_offsets=True,
            enable_automatic_punctuation=False,
            verbatim_transcripts=True,
            sample_rate_hertz=audio.sample_rate,
            audio_channel_count=audio.channels
        )

        # NOT SUPPORTED
        # if config.separate_speaker_per_channel and (audio.channels > 1):
        #     riva_config.enable_separate_recognition_per_channel = True

        response = self.client.offline_recognize(
            audio.byte_array_content, riva_config
        )
        word_list = []
        # print(response)
        for result in response.results:
            for alternative in result.alternatives:
                for word in alternative.words:
                    word_list.append(
                        Word(text=word.word, start=word.start_time, end=word.end_time, speaker=1)
                    )
                break
        if convert_audio:
            audio.delete()

        return RecognizeResult(transcript=None, words=word_list)

    def stream(self, stream: Stream, config: Config):
        # don't need to support now
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("RIVA ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        ssl_cert = kwargs.get("ssl_cert")
        use_ssl = kwargs.get("use_ssl")
        if use_ssl is None:
            use_ssl = False
        server = kwargs.get("server")
        if server is None:
            raise ConfigurationException("RIVA ASR: Specify server arg")
        auth = riva.client.Auth(ssl_cert, use_ssl, server)
        client = riva.client.ASRService(auth)
        return RivaClient(client)
