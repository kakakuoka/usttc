from abc import ABC, abstractmethod

# ASR will only return these punctuations
PUNC_LIST = set(",.?!;")


class ComparablePhrase(ABC):
    def __init__(self):
        pass

    @property
    @abstractmethod
    def clean_text(self):
        pass

    def __eq__(self, other):
        if isinstance(other, ComparablePhrase):
            return self.clean_text == other.clean_text
        if isinstance(other, str):
            return self.clean_text == other
        return False
