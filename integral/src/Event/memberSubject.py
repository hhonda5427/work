

from abc import ABCMeta, abstractmethod

from Event.observer import Observer

# class DataForm(Enum):
#     kinmuDF = auto()
#     yakinDF = auto()
#     member = auto()


class memberUpdateGenerator(metaclass=ABCMeta):
    """
    member要素の変化を報告する親クラス
    """

    def __init__(self) -> None:
        self.__observers: list[Observer] = []  # __を付けることでprivate変数にできる

    def addObserber(self, observer) -> None:
        self.__observers.append(observer)

    def removeObserber(self, observer) -> None:
        self.__observers.remove(observer)

    def notifyObseber(self):
        for observer in self.__observers:
            observer.update(self)

    @abstractmethod
    def getKinmuDF(self):
        pass

    @abstractmethod
    def getYakinDF(self):
        pass
