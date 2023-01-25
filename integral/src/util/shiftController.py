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
            f'変更申請: row:{index.row()}, column:{index.column()}, value:{value}, from:{fromClass}')
        """
        <<fromClass: Model4Kinmu>>
        index.row() -> uid
        index.column() -> day
        value -> job
        """
        if fromClass == "ShiftModel":
            print(f'呼び出されました:{self.updateMember.__name__}')
            uidList = list(self.shiftCtrl.members.keys())
            print(uidList)
            self.shiftCtrl.members[uidList[index.row(
            )]].jobPerDay[self.shiftCtrl.day_previous_next[index.column()]] = 3
            print(f'uidList[index.row()]: {uidList[index.row()]}, self.shiftCtrl.day_previous_next[index.column()]:{self.shiftCtrl.day_previous_next[index.column()]}')
            print(self.shiftCtrl.members[uidList[index.row()]].jobPerDay[self.shiftCtrl.day_previous_next[index.column()]] == self.shiftCtrl.members[4].jobPerDay[(2023, 4, 2, 6)])
            print(f'大元のmember: {self.shiftCtrl.members[2].jobPerDay[(2023, 4, 2, 6)]}')
            self.notifyObseber()

    def getKinmuDF(self):
        print(f'呼び出されました:{self.getKinmuDF.__name__}')
        tmp = self.shiftCtrl.getKinmuForm(DataName.kinmu)
        print(f'変更されているであろうDF:{tmp.loc[:60,["2023-04-02", "2023-04-03"]]}')
        print(f'大元のmember: {self.shiftCtrl.members[4].jobPerDay[(2023, 4, 2, 6)]}')
        return self.shiftCtrl.getKinmuForm(DataName.kinmu)

    def getYakinDF(self):
        print(f'呼び出されました:{self.getYakinDF.__name__}')
        return self.shiftCtrl.getYakinForm()
