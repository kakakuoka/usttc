import base64
import os
from uni_transcribe.audio_transcoder.audio_file import AudioFile
from uni_transcribe.exceptions.exceptions import AudioException


class Audio:
    def __init__(self, file):
        self._file = file
        self.audio_file = AudioFile(file)
        if not self.audio_file.is_valid_audio():
            raise AudioException("Audio file is not valid")

    @property
    def file_size(self):
        return os.path.getsize(self._file)

    @property
    def file_extension(self):
        return os.path.splitext(self._file)[-1]

    @property
    def duration(self):
        return self.audio_file.duration

    @property
    def channels(self):
        return self.audio_file.channels

    @property
    def codec(self):
        return self.audio_file.codec

    @property
    def sample_rate(self):
        return self.audio_file.sample_rate

    @property
    def byte_array_content(self):
        if self._file:
            with open(self._file, "rb") as f:
                return f.read()
        return None

    @property
    def base64_content(self):
        byte_array_content = self.byte_array_content
        if byte_array_content is not None:
            return base64.b64encode(byte_array_content).decode()
        return None

    @property
    def file(self):
        return self._file


class Config:
    def __init__(self, language=None, google_storage_bucket=None, s3_bucket=None):
        self.language = language
        self.google_storage_bucket = google_storage_bucket
        self.s3_bucket = s3_bucket


class Result:
    def __init__(self, transcript, confidence):
        self._transcript = transcript
        self._confidence = confidence

    @property
    def transcript(self):
        if self._transcript:
            return self._transcript
        return ""
