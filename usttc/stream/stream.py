from abc import abstractmethod, ABC


class Stream(ABC):
    @abstractmethod
    def generator(self):
        pass
