from uni_transcribe.asr_client.asr_client import AsrClient
from uni_transcribe.config import Config
from uni_transcribe.audio.audio_file import AudioFile
from uni_transcribe.result.recognize_result import RecognizeResult
from uni_transcribe.result.word import Word
from uni_transcribe.exceptions.exceptions import ConfigurationException
from rev_ai import apiclient, JobStatus
import time


class RevClient(AsrClient):
    def __init__(self, client):
        self.client = client

    def recognize(self, config: Config, audio: AudioFile):
        job = self.client.submit_job_local_file(
            audio.file,
            skip_diarization=True
        )

        while True:
            time.sleep(5)
            job_details = self.client.get_job_details(job.id)
            if job_details.status == JobStatus.TRANSCRIBED:
                json_result = self.client.get_transcript_json(job.id)
                # print(json_result)
                transcript = ""
                words = []
                monologue = json_result["monologues"][0]
                for element in monologue["elements"]:
                    transcript += element["value"]
                    if element["type"] == "text":
                        words.append(
                            Word(
                                text=element["value"], confidence=element["confidence"],
                                start=element["ts"] * 1000,
                                end=element["end_ts"] * 1000
                            )
                        )
                break
            elif job_details.status == JobStatus.FAILED:
                transcript = ""
                words = None
                break

        self.client.delete_job(job.id)
        return RecognizeResult(transcript=transcript, words=words)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Rev.ai ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        client = apiclient.RevAiAPIClient(key)
        return RevClient(client)
