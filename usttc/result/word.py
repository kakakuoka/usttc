from usttc.result.text_unit import TextUnit


class Word(TextUnit):
    def __init__(self, text, confidence=1, start=None, end=None, duration=None, speaker=None):
        super().__init__(text, confidence, start, end, duration, speaker)

    def __repr__(self):
        return "[Word] Speaker-{}: {} [{} : {}] (conf: {})".format(
            self.speaker, self.text, self.start, self.end, self.confidence
        )

    @property
    def speaker(self):
        if self._speaker is not None:
            return self._speaker
        return 0

    @speaker.setter
    def speaker(self, s):
        self._speaker = s

    def to_json(self):
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "confidence": self.confidence,
            "speaker": self.speaker
        }

    @staticmethod
    def from_json(json_dict):
        return Word(
            text=json_dict.get("text"),
            confidence=json_dict.get("confidence"),
            start=json_dict.get("start"),
            end=json_dict.get("end"),
            duration=json_dict.get("duration"),
            speaker=json_dict.get("speaker")
        )
