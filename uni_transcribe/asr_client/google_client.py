from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile, AudioFormat
from uni_transcribe.result.recognize_result import RecognizeResult
from uni_transcribe.result.word import Word
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
from uni_transcribe.utils import generate_random_str
from uni_transcribe.stream.stream_results import StreamResult, StreamResults
from uni_transcribe.stream.stream import Stream
from google.cloud import speech
from google.cloud import storage

AUDIO_DURATION_LIMIT = 480 * 60


class GoogleClient(AsrClient):
    def __init__(self, client, storage_client):
        self.client = client
        self.storage_client = storage_client

    def recognize(self, config: Config, audio: AudioFile):
        if audio.duration >= AUDIO_DURATION_LIMIT:
            raise AudioException("Google does not support audio longer than 480 minutes")

        convert_audio = False
        if audio.codec not in {
            AudioFormat.LINEAR16, AudioFormat.FLAC, AudioFormat.MULAW, AudioFormat.AMR
        }:
            audio = audio.convert()
            convert_audio = True

        if audio.duration < 60:
            recog_audio = speech.RecognitionAudio(
                content=audio.byte_array_content
            )
            result = self._async_recognize(config, audio, recog_audio)
        else:
            if not config.google_storage_bucket:
                raise ConfigurationException("Please provide google_storage_bucket in the config for long file")
            blob = self._upload_to_google_storage(config.google_storage_bucket, audio)
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
            model="video",
            use_enhanced=True,
            enable_word_time_offsets=True
        )

        if config.diarization:
            min_spk_count = max(config.diarization[0], 1)
            max_spk_count = config.diarization[1]
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True, min_speaker_count=min_spk_count, max_speaker_count=max_spk_count
            )
            recognition_config.diarization_config = diarization_config

        operation = self.client.long_running_recognize(config=recognition_config, audio=recog_audio)
        response = operation.result()

        transcripts = []
        words = []
        for result in response.results:
            alternative = result.alternatives[0]
            transcripts.append(alternative.transcript.strip())
        last_result = response.results[-1]
        for w in last_result.alternatives[0].words:
            start = w.start_time.total_seconds() * 1000
            end = w.end_time.total_seconds() * 1000
            words.append(Word(text=w.word, start=start, end=end, speaker=w.speaker_tag))

        return RecognizeResult(transcript=" ".join(transcripts), words=words)

    def _upload_to_google_storage(self, bucket_name, audio: AudioFile):
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob("{}{}".format(generate_random_str(20), audio.file_extension))
        blob.upload_from_filename(audio.file)
        return blob

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        client = speech.SpeechClient.from_service_account_file(filename)
        storage_client = storage.Client.from_service_account_json(filename)
        return GoogleClient(client, storage_client)

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        raise ConfigurationException("Google ASR: Use key file authentication")
