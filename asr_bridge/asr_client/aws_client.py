from asr_bridge.asr_client.asr_client import AsrClient
from asr_bridge.messages import *
from asr_bridge.exceptions.exceptions import ConfigurationException, AudioException
import time
import boto3
import requests
from asr_bridge.utils import generate_random_str


class AwsClient(AsrClient):
    def __init__(self, s3_client, transcribe_client):
        self.s3_client = s3_client
        self.transcribe_client = transcribe_client

    def recognize(self, config: Config, audio: Audio):
        if not config.s3_bucket:
            raise ConfigurationException("Please provide s3_bucket in the config")

        s3_object_name = "{}{}".format(generate_random_str(20), audio.file_extension)
        self.s3_client.upload_file(
            audio.file, config.s3_bucket, s3_object_name
        )

        job_name = "job-{}".format(generate_random_str(20))
        job_uri = "s3://{}/{}".format(config.s3_bucket, s3_object_name)
        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='wav',
            LanguageCode=config.language
        )

        while True:
            status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                r = requests.get(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                transcript = r.json()['results']['transcripts'][0]['transcript']
                break
            elif status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
                transcript = ""
                break
            time.sleep(5)
        self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
        self.s3_client.delete_object(Bucket=config.s3_bucket, Key=s3_object_name)
        return Result(transcript=transcript, confidence=1)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Google ASR: Use key authentication")

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
