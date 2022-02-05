from usttc.ensemble.comparable_phrase import ComparablePhrase, PUNC_LIST


class ComparableDiffWord(ComparablePhrase):
    """
    Different words from multiple providers
    """
    def __init__(self, provider_word_list_map):
        super().__init__()
        self.provider_word_list_map = provider_word_list_map

    def __str__(self):
        str_d = dict()
        for provider, words in self.provider_word_list_map.items():
            str_d[provider.name] = [word.text for word in words]
        return str(str_d)

    @property
    def clean_text(self):
        return None
