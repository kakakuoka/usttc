import ffmpeg
from enum import Enum


class AudioFile:
    def __init__(self, file_path):
        self.valid = False
        try:
            probe_dict = ffmpeg.probe(file_path)
            self.duration = float(probe_dict["format"]["duration"])
            audio_stream = None
            for stream in probe_dict["streams"]:
                if stream.get("codec_type") == "audio":
                    audio_stream = stream
                    break
            if audio_stream:
                self.channels = int(audio_stream["channels"])
                self.sample_rate = int(audio_stream["sample_rate"])
                self.codec = self._get_audio_format(audio_stream["codec_name"])
                self.valid = True
        except:
            pass

    def is_valid_audio(self):
        return self.valid

    @staticmethod
    def _get_audio_format(codec_name):
        if codec_name == "pcm_s16le":
            return AudioFormat.LINEAR16
        return None


class AudioFormat(Enum):
    LINEAR16 = 1
    FLAC = 2
    MULAW = 3
    AMR = 4
    AMR_WB = 5
    OGG_OPUS = 6
