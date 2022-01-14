from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile, AudioFormat
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.exceptions.exceptions import ConfigurationException, AudioException
from usttc.asr_client.asr_provider import AsrProvider
import time
import boto3
import requests
from usttc.utils.utils import generate_random_str


AUDIO_DURATION_LIMIT = 4 * 60 * 60
FILE_SIZE_LIMIT = 2 * 1024 * 1024 * 1024


class AwsClient(AsrClient):
    provider = AsrProvider.AMAZON_AWS

    def __init__(self, s3_client, transcribe_client, s3_bucket):
        self.s3_client = s3_client
        self.transcribe_client = transcribe_client
        self.s3_bucket = s3_bucket

    def recognize(self, audio: AudioFile, config: Config = Config()):

        if audio.duration > AUDIO_DURATION_LIMIT:
            raise AudioException("AWS does not support audio longer than 4 hours")

        convert_audio = False
        if audio.codec not in {
            AudioFormat.LINEAR16, AudioFormat.FLAC, AudioFormat.MULAW, AudioFormat.AMR, AudioFormat.MP3, AudioFormat.MP4
        }:
            audio = audio.convert()
            convert_audio = True

        if audio.file_size > FILE_SIZE_LIMIT:
            if convert_audio:
                audio.delete()
            raise AudioException("AWS does not support audio larger than 2GB")

        s3_object_name = "{}{}".format(generate_random_str(20), audio.file_extension)
        self.s3_client.upload_file(
            audio.file, self.s3_bucket, s3_object_name
        )

        job_name = "job-{}".format(generate_random_str(20))
        job_uri = "s3://{}/{}".format(self.s3_bucket, s3_object_name)

        settings = {}
        if config.diarization:
            max_spk_count = config.diarization[1]
            settings["MaxSpeakerLabels"] = min(max(max_spk_count, 2), 10)
            settings["ShowSpeakerLabels"] = True
        if config.separate_speaker_per_channel and audio.channels > 1:
            settings["ChannelIdentification"] = True

        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=audio.file_extension_no_dot,
            LanguageCode=config.language,
            Settings=settings
        )

        def _process_items(items, spk_id=None, _speaker_map=None):
            words = []
            for i in items:
                if i["type"] == "pronunciation":
                    alternatives = i["alternatives"]
                    if alternatives:
                        speaker_id = spk_id
                        if (speaker_id is None) and (_speaker_map is not None):
                            speaker_id = _speaker_map.get((i["start_time"], i["end_time"]))
                        word = Word(
                            text=alternatives[0]["content"],
                            confidence=alternatives[0]["confidence"],
                            start=float(i["start_time"]) * 1000,
                            end=float(i["end_time"]) * 1000,
                            speaker=speaker_id
                        )
                        words.append(word)
                elif (i["type"] == "punctuation") and words:
                    alternatives = i["alternatives"]
                    if alternatives:
                        content = alternatives[0]["content"]
                        words[-1].append_text(content)
            return words

        while True:
            status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                r = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                results = r.json()['results']
                word_list = []
                # multi-channel
                if ("channel_labels" in results) and ("channels" in results["channel_labels"]):
                    for channel in results["channel_labels"]["channels"]:
                        speaker = channel["channel_label"]
                        word_list += _process_items(channel["items"], spk_id=speaker)
                else:
                    # generate speaker map
                    speaker_map = dict()
                    if ("speaker_labels" in results) and ("segments" in results["speaker_labels"]):
                        for segment in results["speaker_labels"]["segments"]:
                            for item in segment["items"]:
                                speaker_map[(item["start_time"], item["end_time"])] = item["speaker_label"]
                    word_list += _process_items(results["items"], _speaker_map=speaker_map)
                break
            elif status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
                word_list = None
                break
            time.sleep(5)
        self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
        self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_object_name)
        if convert_audio:
            audio.delete()
        return RecognizeResult(words=word_list)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("AWS ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        aws_access_key_id = key
        aws_secret_access_key = kwargs.get("aws_secret_access_key")
        if not aws_secret_access_key:
            raise ConfigurationException("AWS ASR: Specify aws_secret_access_key arg")
        region_name = kwargs.get("region_name")
        if not region_name:
            raise ConfigurationException("AWS ASR: Specify region_name arg")
        s3_bucket = kwargs.get("s3_bucket")
        if not s3_bucket:
            raise ConfigurationException("AWS ASR: Specify s3_bucket arg")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name)
        transcribe_client = boto3.client(
            'transcribe',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name)
        return AwsClient(s3_client, transcribe_client, s3_bucket)
