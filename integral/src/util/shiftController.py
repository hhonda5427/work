from PyQt5.QtCore import QModelIndex

from Event.memberSubject import memberUpdateGenerator
from util.dataReader import DataReader
from util.dataSender import DataSender, DataName


class Singleton():
     def __new__(cls, *arg, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class ShiftController(DataReader, DataSender, Singleton):
    def __init__(self):
        super().__init__()


class ShiftChannel(memberUpdateGenerator):
    """
    memberクラスの変化報告、model変化の受付
    """
    def __init__(self, shiftCtrl: ShiftController) -> None:
        super().__init__()
        self.shiftCtrl = shiftCtrl

    def updateMember(self, index: QModelIndex, value, fromClass):
        print(
            f'row:{index.row()}, column:{index.column()}, value:{value}, from:{fromClass}')
        """
        <<fromClass: Model4Kinmu>>
        index.row() -> uid
        index.column() -> day
        value -> job
        """
        if fromClass == "ShiftModel":

            uidList = list(self.shiftCtrl.members.keys())
            print(f'書き換え前:{self.shiftCtrl.members[uidList[index.row()]].jobPerDay[self.shiftCtrl.day_previous_next[index.column()]]}')
            self.shiftCtrl.members[uidList[index.row(
            )]].jobPerDay[self.shiftCtrl.day_previous_next[index.column()]] = value

            print(f'書き換え後:{self.shiftCtrl.members[uidList[index.row()]].jobPerDay[self.shiftCtrl.day_previous_next[index.column()]]}')
            self.notifyObseber()

    def getKinmuDF(self):
        print(f'呼び出されました:{self.getKinmuDF.__name__}')
        return self.shiftCtrl.getKinmuForm(DataName.kinmu)

    def getYakinDF(self):
        print(f'呼び出されました:{self.getYakinDF.__name__}')
        return self.shiftCtrl.getYakinForm()
