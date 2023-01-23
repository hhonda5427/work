from PyQt5.QtCore import QModelIndex

from Event.memberSubject import memberUpdateGenerator
from util.dataReader import DataReader
from util.dataSender import DataSender, DataName


class ShiftController(DataReader, DataSender):
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
        if fromClass == "Model4Kinmu":
            print(f'呼び出されました:{self.updateMember.__name__}')
            uidList = list(self.shiftCtrl.members.keys())
            self.shiftCtrl.members[uidList[index.row(
            )]].jobPerDay[self.shiftCtrl.day_previous_next[index.column()]] = value
            self.notifyObseber()

    def getKinmuDF(self):
        print(f'呼び出されました:{self.getKinmuDF.__name__}')
        return self.shiftCtrl.getKinmuForm(DataName.kinmu)

    def getYakinDF(self):
        print(f'呼び出されました:{self.getYakinDF.__name__}')
        return self.shiftCtrl.getYakinForm()
