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
