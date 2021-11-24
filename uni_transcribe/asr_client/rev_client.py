from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.messages import *
from uni_transcribe.exceptions.exceptions import ConfigurationException, AudioException
from rev_ai import apiclient, JobStatus
import time


class RevClient(AsrClient):
    def __init__(self, client):
        self.client = client

    def recognize(self, config: Config, audio: Audio):
        job = self.client.submit_job_local_file(
            audio.file,
            skip_diarization=True
        )

        while True:
            time.sleep(5)
            job_details = self.client.get_job_details(job.id)
            if job_details.status == JobStatus.TRANSCRIBED:
                json_result = self.client.get_transcript_json(job.id)
                transcript = ""
                for monologue in json_result["monologues"]:
                    for element in monologue["elements"]:
                        transcript += element["value"]
                break
            elif job_details.status == JobStatus.FAILED:
                transcript = ""
                break

        self.client.delete_job(job.id)
        return Result(transcript=transcript, confidence=1)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Rev.ai ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        client = apiclient.RevAiAPIClient(key)
        return RevClient(client)
