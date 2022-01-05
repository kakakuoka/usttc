from usttc.result.word import Word
from usttc.ensemble.comparable_phrase import ComparablePhrase, PUNC_LIST


class ComparableWord(ComparablePhrase):
    def __init__(self, word: Word):
        super().__init__()
        self.text = word.text
        self.start = word.start
        self.end = word.end
        self.duration = word.duration
        self.confidence = word.confidence
        self.speaker = word.speaker
        self._clean_text = None

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    @property
    def clean_text(self):
        if self._clean_text is None:
            ct = self.text.lower()
            if ct[-1] in PUNC_LIST:
                ct = ct[:-1]
            self._clean_text = ct
        return self._clean_text


