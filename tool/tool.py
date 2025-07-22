from abc import abstractmethod, ABC


class Tool(ABC):

    @abstractmethod
    def run(self):
        pass
