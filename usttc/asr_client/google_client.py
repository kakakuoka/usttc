from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile, AudioFormat
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.exceptions.exceptions import ConfigurationException, AudioException
from usttc.utils.utils import generate_random_str
from usttc.stream.stream_results import StreamResult, StreamResults
from usttc.stream.stream import Stream
from google.cloud import speech
from google.cloud import storage
from usttc.asr_client.asr_provider import AsrProvider

AUDIO_DURATION_LIMIT = 480 * 60


class GoogleClient(AsrClient):
    provider = AsrProvider.GOOGLE

    def __init__(self, client, storage_client, google_storage_bucket, google_model):
        self.client = client
        self.storage_client = storage_client
        self.google_storage_bucket = google_storage_bucket
        self.google_model = google_model

    def recognize(self, audio: AudioFile, config: Config = Config()):
        if audio.duration >= AUDIO_DURATION_LIMIT:
            raise AudioException("Google does not support audio longer than 480 minutes")

        convert_audio = False
        if audio.channels > 1 and not config.separate_speaker_per_channel:
            audio = audio.convert(to_mono=True)
            convert_audio = True
        elif (
                audio.codec not in {AudioFormat.LINEAR16, AudioFormat.FLAC, AudioFormat.MULAW, AudioFormat.AMR}
            ) or (
                (audio.codec not in {AudioFormat.LINEAR16, AudioFormat.FLAC})
                and (audio.channels > 1)
                and config.separate_speaker_per_channel
            ):
            audio = audio.convert()
            convert_audio = True

        if audio.duration < 60:
            recog_audio = speech.RecognitionAudio(
                content=audio.byte_array_content
            )
            result = self._async_recognize(config, audio, recog_audio)
        else:
            blob = self._upload_to_google_storage(self.google_storage_bucket, audio)
            gs_url = "gs://{}/{}".format(blob.bucket.name, blob.name)
            recog_audio = speech.RecognitionAudio()
            recog_audio.uri = gs_url
            result = self._async_recognize(config, audio, recog_audio)
            blob.delete()

        if convert_audio:
            audio.delete()
        return result

    def stream(self, stream: Stream, config: Config):

        recog_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=config.language,
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=recog_config,
            interim_results=True
        )

        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = self.client.streaming_recognize(streaming_config, requests)

        def parse_response():
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                if not result.is_final:
                    yield StreamResult(transcript, False)
                else:
                    yield StreamResult(transcript, True)

        return StreamResults(parse_response())

    def _async_recognize(self, config: Config, audio: AudioFile, recog_audio):
        recognition_config = speech.RecognitionConfig(
            encoding=audio.codec.name,
            sample_rate_hertz=audio.sample_rate,
            language_code=config.language,
            model=self.google_model,
            use_enhanced=True,
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True
        )

        if config.diarization:
            min_spk_count = config.diarization[0]
            max_spk_count = config.diarization[1]
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True, min_speaker_count=min_spk_count, max_speaker_count=max_spk_count
            )
            recognition_config.diarization_config = diarization_config

        if config.separate_speaker_per_channel and audio.channels > 1:
            recognition_config.enable_separate_recognition_per_channel = True
            recognition_config.audio_channel_count = audio.channels

        if config.hints:
            speech_context = speech.SpeechContext(
                phrases=config.hints
            )
            recognition_config.speech_contexts = [speech_context]

        operation = self.client.long_running_recognize(config=recognition_config, audio=recog_audio)
        response = operation.result()
        words = []
        for current_result in response.results:
            current_channel_tag = current_result.channel_tag
            for w in current_result.alternatives[0].words:
                start = w.start_time.total_seconds() * 1000
                end = w.end_time.total_seconds() * 1000
                if current_channel_tag:
                    speaker = current_channel_tag
                else:
                    speaker = w.speaker_tag
                if config.diarization and not speaker:
                    continue
                words.append(Word(text=w.word, start=start, end=end, speaker=speaker))

        return RecognizeResult(transcript=None, words=words)

    def _upload_to_google_storage(self, bucket_name, audio: AudioFile):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob("{}{}".format(generate_random_str(20), audio.file_extension))
        blob.upload_from_filename(audio.file)
        return blob

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        google_storage_bucket = kwargs.get("google_storage_bucket")
        if not google_storage_bucket:
            raise ConfigurationException("Google ASR: Specify google_storage_bucket arg")
        google_model = kwargs.get("google_model")
        if google_model is None:
            google_model = "video"
        client = speech.SpeechClient.from_service_account_file(filename)
        storage_client = storage.Client.from_service_account_json(filename)
        return GoogleClient(client, storage_client, google_storage_bucket, google_model)

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        raise ConfigurationException("Google ASR: Use key file authentication")
