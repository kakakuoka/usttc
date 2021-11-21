import base64


class Audio:
    def __init__(self, file=None, uri=None):
        self._file = file
        self._uri = uri

    @property
    def uri(self):
        return self._uri

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


class Config:
    def __init__(self, encoding=None, sample_rate=None, language=None):
        self.encoding = encoding
        self.sample_rate = sample_rate
        self.language = language


class Result:
    def __init__(self, alternatives):
        self.alternatives = alternatives

    def get_best_transcript(self):
        if self.alternatives:
            return self.alternatives[0].transcript
        return ""


class Alternative:
    def __init__(self, transcript, confidence):
        self.transcript = transcript
        self.confidence = confidence
