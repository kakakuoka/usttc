from usttc.exceptions.exceptions import ConfigurationException


class Config:
    def __init__(self, language: str = "en-US", diarization: tuple = None, separate_speaker_per_channel: bool = False,
                 hints=None):
        """
        :param language:
        :param diarization: To enable diarization, set to tuple (min_speaker_count, max_speaker_count)
        :param separate_speaker_per_channel:
        :param hints: a list of words as hints
        """
        self.language = language
        if diarization and separate_speaker_per_channel:
            raise ConfigurationException(
                "Cannot configure diarization and separate_recognition_per_channel together. "
                "If you want to detect multiple speakers from mono audio, please configure diarization. "
                "If the audio has multiple channels, please use separate_speaker_per_channel"
            )
        self.diarization = None
        if diarization:
            if (len(diarization) != 2) or \
                    (not isinstance(diarization[0], int)) or (not isinstance(diarization[1], int)) or \
                    (diarization[0] > diarization[1]) or (diarization[0] < 1):
                raise ConfigurationException("Diarization config is invalid")
            if diarization[1] > 1:
                self.diarization = diarization
        self.separate_speaker_per_channel = separate_speaker_per_channel
        self.hints = hints
