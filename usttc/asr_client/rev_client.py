from usttc.asr_client.asr_client import AsrClient
from usttc.config import Config
from usttc.audio.audio_file import AudioFile
from usttc.result.recognize_result import RecognizeResult
from usttc.result.word import Word
from usttc.exceptions.exceptions import ConfigurationException
from usttc.asr_client.asr_provider import AsrProvider
from rev_ai import apiclient, JobStatus
import time


class RevClient(AsrClient):
    provider = AsrProvider.REV

    def __init__(self, client):
        self.client = client

    def recognize(self, audio: AudioFile, config: Config = Config()):
        speaker_channels_count = None
        if config.separate_speaker_per_channel and audio.channels > 1:
            speaker_channels_count = audio.channels
        job = self.client.submit_job_local_file(
            audio.file,
            skip_diarization=(config.diarization is None),
            speaker_channels_count=speaker_channels_count,
            language=config.language[:2]
        )

        while True:
            time.sleep(5)
            job_details = self.client.get_job_details(job.id)
            if job_details.status == JobStatus.TRANSCRIBED:
                json_result = self.client.get_transcript_json(job.id)
                # transcript = ""
                words = []
                for monologue in json_result["monologues"]:
                    speaker = monologue["speaker"]
                    for element in monologue["elements"]:
                        # transcript += element["value"]
                        if element["type"] == "text":
                            words.append(
                                Word(
                                    text=element["value"], confidence=element["confidence"],
                                    start=element["ts"] * 1000,
                                    end=element["end_ts"] * 1000,
                                    speaker=speaker
                                )
                            )
                        elif (element["type"] == "punct") and words:
                            value_strip = element["value"].strip()
                            if value_strip:
                                words[-1].append_text(value_strip)
                break
            elif job_details.status == JobStatus.FAILED:
                # transcript = ""
                words = None
                break

        self.client.delete_job(job.id)
        return RecognizeResult(words=words)

    def stream(self):
        pass

    @staticmethod
    def from_key_file(filename: str, *args, **kwargs):
        raise ConfigurationException("Rev.ai ASR: Use key authentication")

    @staticmethod
    def from_key(key: str, *args, **kwargs):
        client = apiclient.RevAiAPIClient(key)
        return RevClient(client)
