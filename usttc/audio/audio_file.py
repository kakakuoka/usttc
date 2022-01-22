import ffmpeg
from enum import Enum
import base64
import os
from usttc.utils.utils import generate_random_str
from usttc.exceptions.exceptions import AudioException


class AudioFile:
    def __init__(self, file_path):
        self._file = file_path
        self._valid = False
        try:
            probe_dict = ffmpeg.probe(file_path)
            # print(probe_dict)
            self._duration = float(probe_dict["format"]["duration"])
            audio_stream = None
            for stream in probe_dict["streams"]:
                if stream.get("codec_type") == "audio":
                    audio_stream = stream
                    break
            if audio_stream:
                self._channels = int(audio_stream["channels"])
                if self._channels > 2:
                    AudioException("Only support mono or stereo audio")
                self._sample_rate = int(audio_stream["sample_rate"])
                self._codec = self._get_audio_format(audio_stream["codec_name"], self.file_extension_no_dot)
                if self._codec:
                    self._valid = True
        except AudioException as e:
            raise e
        except:
            pass
        if not self._valid:
            raise AudioException("Audio file is not valid")

    def convert(self, to="wav", sample_rate=16000, to_mono=False):
        file_dir, _ = os.path.split(self._file)
        new_file_path = os.path.join(file_dir, generate_random_str(10) + ".{}".format(to))
        stream = ffmpeg.input(self._file)
        kp = {'ar': str(sample_rate)}
        if to_mono:
            kp['ac'] = '1'
        stream = ffmpeg.output(stream, new_file_path, **kp)
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        return AudioFile(file_path=new_file_path)

    def delete(self):
        os.remove(self._file)

    @property
    def file_size(self):
        return os.path.getsize(self._file)

    @property
    def file_extension(self):
        return os.path.splitext(self._file)[-1]

    @property
    def file_extension_no_dot(self):
        return self.file_extension.strip(".")

    @property
    def duration(self):
        return self._duration

    @property
    def channels(self):
        return self._channels

    @property
    def codec(self):
        return self._codec

    @property
    def sample_rate(self):
        return self._sample_rate

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

    @staticmethod
    def _get_audio_format(codec_name, ext):
        format_map = {
            "pcm_s16le": AudioFormat.LINEAR16,
            "flac": AudioFormat.FLAC,
            "pcm_mulaw": AudioFormat.MULAW,
            "amr_nb": AudioFormat.AMR,
            "mp3": AudioFormat.MP3
        }
        if codec_name in format_map:
            return format_map[codec_name]
        if codec_name == "aac" and ext == "mp4":
            return AudioFormat.MP4
        return AudioFormat.OTHERS


class AudioFormat(Enum):
    OTHERS = 1
    LINEAR16 = 2
    FLAC = 3
    MULAW = 4
    AMR = 5
    MP3 = 6
    MP4 = 7
