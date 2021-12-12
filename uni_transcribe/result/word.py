

class Word:
    def __init__(self, text, confidence=1, start=None, end=None, duration=None, speaker=None):
        self._text = text
        self._confidence = confidence
        self._speaker = speaker
        self._start = int(start)
        if (end is None) and (duration is None):
            raise ValueError("Both end and duration are None")
        if duration is None:
            self._end = int(end)
            self._duration = max(0, self._end - self._start)
        elif end is None:
            self._duration = int(duration)
            self._end = self._start + self._duration
        else:
            self._end = int(end)
            self._duration = int(duration)
            if self._start + self._duration != self._end:
                raise ValueError("start + duration != end")

    def __repr__(self):
        return "{}: {} [{} : {}]".format(self.speaker, self.text, self.start, self.end)

    @property
    def text(self):
        return self._text

    @property
    def confidence(self):
        return self._confidence

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def duration(self):
        return self._duration

    @property
    def speaker(self):
        if self._speaker is not None:
            return self._speaker
        return 0

    @speaker.setter
    def speaker(self, s):
        self._speaker = s
