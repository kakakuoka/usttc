from usttc.result.recognize_result import RecognizeResult
from usttc.ensemble.comparable_word import ComparableWord


class ComparableResult:
    """
    The result that can compare with another ComparableResult
    Each ComparableResult contains a list of ComparablePhrase
    """
    def __init__(self, result: RecognizeResult = None, provider=None):
        self.phrases = []
        if result and result.words:
            for word in result.words:
                self.phrases.append(ComparableWord({provider: word}))

    def __len__(self):
        return len(self.phrases)

    def __getitem__(self, item):
        return self.phrases[item]

    def __iter__(self):
        return self.phrases.__iter__()
