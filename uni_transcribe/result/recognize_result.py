

class RecognizeResult:
    def __init__(self, transcript=None, words=None):
        self._transcript = transcript
        if self._transcript is not None:
            self._transcript = self._transcript.strip()
        self._words = words

    @property
    def transcript(self):
        if self._transcript:
            return self._transcript
        if self._words:
            return " ".join([i.text for i in self._words])
        return ""

    @property
    def words(self):
        if self._words:
            return self._words
        return None
