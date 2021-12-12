import string


class RecognizeResult:
    def __init__(self, transcript=None, words=None):
        self._transcript = transcript
        if self._transcript is not None:
            self._transcript = self._transcript.strip()
        self._words = words
        self.post_process_done = False

    @property
    def transcript(self):
        if self._transcript:
            return self._transcript
        if self.words:
            return " ".join([i.text for i in self.words])
        return ""

    @property
    def words(self):
        if self._words:
            if not self.post_process_done:
                self._post_process_word()
            return self._words
        return None

    def _post_process_word(self):
        self._words.sort(key=lambda x: x.start)
        current_spk_id_map = dict()
        for word in self._words:
            speaker = word.speaker
            if speaker in current_spk_id_map:
                word.speaker = current_spk_id_map.get(speaker)
            else:
                new_id = string.ascii_uppercase[len(current_spk_id_map)]
                current_spk_id_map[speaker] = new_id
                word.speaker = new_id

        self.post_process_done = True
