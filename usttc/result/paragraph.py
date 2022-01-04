from usttc.result.text_unit import TextUnit


class Paragraph(TextUnit):
    def __init__(self, text, confidence=1, start=None, end=None, duration=None, speaker=None):
        super().__init__(text, confidence, start, end, duration, speaker)

    def __repr__(self):
        return "[Paragraph] Speaker-{}: {} [{} : {}] (conf: {})".format(
            self.speaker, self.text, self.start, self.end, self.confidence
        )
