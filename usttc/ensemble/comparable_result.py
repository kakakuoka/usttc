from usttc.result.recognize_result import RecognizeResult
from usttc.ensemble.comparable_word import ComparableWord


class ComparableResult:
    def __init__(self, result: RecognizeResult):
        self.phrases = []
        if result and result.words:
            for word in result.words:
                self.phrases.append(ComparableWord(word))

    def __len__(self):
        return len(self.phrases)

    def __iter__(self):
        return self.phrases.__iter__()
