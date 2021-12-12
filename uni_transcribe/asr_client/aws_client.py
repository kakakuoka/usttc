from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile, AudioFormat
from uni_transcribe.result.recognize_result import RecognizeResult
from uni_transcribe.result.word import Word
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
import time
import boto3
import requests
from uni_transcribe.utils import generate_random_str


AUDIO_DURATION_LIMIT = 4 * 60 * 60
FILE_SIZE_LIMIT = 2 * 1024 * 1024 * 1024


class AwsClient(AsrClient):
    def __init__(self, s3_client, transcribe_client):
        self.s3_client = s3_client
        self.transcribe_client = transcribe_client

    def recognize(self, config: Config, audio: AudioFile):
        if not config.s3_bucket:
            raise ConfigurationException("Please provide s3_bucket in the config")

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
            audio.file, config.s3_bucket, s3_object_name
        )

        job_name = "job-{}".format(generate_random_str(20))
        job_uri = "s3://{}/{}".format(config.s3_bucket, s3_object_name)

        settings = {}
        if config.diarization:
            max_spk_count = config.diarization[1]
            settings["MaxSpeakerLabels"] = min(max(max_spk_count, 2), 10)
            settings["ShowSpeakerLabels"] = True

        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat=audio.file_extension_no_dot,
            LanguageCode=config.language,
            Settings=settings
        )

        while True:
            status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                r = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                results = r.json()['results']
                transcript = results['transcripts'][0]['transcript']

                # generate speaker map
                speaker_map = dict()
                if ("speaker_labels" in results) and ("segments" in results["speaker_labels"]):
                    for segment in results["speaker_labels"]["segments"]:
                        for item in segment["items"]:
                            speaker_map[(item["start_time"], item["end_time"])] = item["speaker_label"]

                words = []
                for i in results["items"]:
                    if i["type"] == "pronunciation":
                        alternatives = i["alternatives"]
                        if alternatives:
                            spk_id = speaker_map.get((i["start_time"], i["end_time"]))
                            word = Word(
                                text=alternatives[0]["content"],
                                confidence=alternatives[0]["confidence"],
                                start=float(i["start_time"]) * 1000,
                                end=float(i["end_time"]) * 1000,
                                speaker=spk_id
                            )
                            words.append(word)

                break
            elif status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
                transcript = ""
                words = None
                break
            time.sleep(5)
        self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
        self.s3_client.delete_object(Bucket=config.s3_bucket, Key=s3_object_name)
        if convert_audio:
            audio.delete()
        return RecognizeResult(transcript=transcript, words=words)

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
        return AwsClient(s3_client, transcribe_client)
