from usttc.ensemble.comparable_phrase import ComparablePhrase, PUNC_LIST


class ComparableWord(ComparablePhrase):
    """
    Single word
    Same word from one or more recognizers
    """
    def __init__(self, provider_word_map, clean_text=None):
        super().__init__()
        self.provider_word_map = provider_word_map
        if clean_text:
            self._clean_text = clean_text
        else:
            for word in self.provider_word_map.values():
                ct = word.text.lower()
                if ct[-1] in PUNC_LIST:
                    ct = ct[:-1]
                self._clean_text = ct
                break

    def __str__(self):
        str_d = dict()
        for provider, word in self.provider_word_map.items():
            str_d[provider.name] = word.text
        return str(str_d)

    @property
    def clean_text(self):
        return self._clean_text
