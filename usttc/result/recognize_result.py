from usttc.result.paragraph import Paragraph
from usttc.result.word import Word


class RecognizeResult:
    def __init__(self, transcript=None, words=None):
        self._transcript = transcript
        if self._transcript is not None:
            self._transcript = self._transcript.strip()
        self._words = words
        self._dialogue = None
        self.post_process_done = False

    @property
    def transcript(self):
        if self._transcript:
            return self._transcript
        if self.words:
            self._transcript = " ".join([i.text for i in self.words])
            return self._transcript
        return ""

    @property
    def words(self):
        if self._words:
            if not self.post_process_done:
                self._post_process_word()
            return self._words
        return None

    @property
    def dialogue(self):
        self._create_dialogue()
        return self._dialogue

    @property
    def pretty_dialogue(self):
        dialogue = self.dialogue
        pretty_text_list = []
        for paragraph in dialogue:
            pretty_text_list.append("Speaker-{} : {}".format(paragraph.speaker, paragraph.text))
        return "\n".join(pretty_text_list)

    def get_dialogue(self, max_gap=None):
        self._create_dialogue(max_gap)
        return self._dialogue

    def _create_dialogue(self, max_gap=None):
        def create_paragraph(word_list):
            text = " ".join([w.text for w in word_list])
            conf = 0
            for w in word_list:
                conf += w.confidence
            conf /= len(word_list)
            return Paragraph(
                text=text, confidence=conf,
                start=word_list[0].start, end=word_list[-1].end, speaker=word_list[0].speaker
            )

        if self._dialogue is None:
            self._dialogue = []
            current_para = []
            for word in self.words:
                if (not current_para) or (
                        (current_para[-1].speaker == word.speaker) and
                        ((not max_gap) or (word.start - current_para[-1].end <= max_gap))
                ):
                    current_para.append(word)
                else:
                    self._dialogue.append(create_paragraph(current_para))
                    current_para = [word]
            if current_para:
                self._dialogue.append(create_paragraph(current_para))

    def to_json(self):
        if self.words:
            json_list = []
            for word in self.words:
                json_list.append(word.to_json())
            return json_list
        return []

    @staticmethod
    def from_json(json_dict):
        words = []
        for i in json_dict:
            words.append(Word.from_json(i))
        return RecognizeResult(words=words)

    def _post_process_word(self):
        self._words.sort(key=lambda x: x.start)
        current_spk_id_map = dict()
        for word in self._words:
            speaker = word.speaker
            if speaker in current_spk_id_map:
                word.speaker = current_spk_id_map.get(speaker)
            else:
                new_id = len(current_spk_id_map)
                current_spk_id_map[speaker] = new_id
                word.speaker = new_id

        self.post_process_done = True
