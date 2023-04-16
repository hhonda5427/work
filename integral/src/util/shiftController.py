from Event.memberSubject import memberUpdateGenerator
from util.dataSender import DataSender, DataName
from decorator.convertTable import ConvertTable

class Singleton():
     def __new__(cls, *arg, **kargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

class ShiftController(DataSender, Singleton):
    def __init__(self):
        super().__init__()


class ShiftChannel(memberUpdateGenerator):
    """
    memberクラスの変化報告、model変化の受付
    """

    def __init__(self, shiftCtrl: ShiftController) -> None:
        super().__init__()
        self.shiftCtrl = shiftCtrl

    def updateMember(self, uid:int, day:str, job:str):
        print(
            f'変更申請: uid: {uid}, day: {day}, job: {job}')
        """
        <<fromClass: Model4Kinmu>>
        index.row() -> uid
        index.column() -> day
        value -> job
        """

        day = tuple([int(daystr) for daystr in day.split('-')])

        print(f'呼び出されました:{self.updateMember.__name__}')
        self.shiftCtrl.members[uid].jobPerDay[day] = ConvertTable.name2Id(job)
        self.notifyObseber()

    def getKinmuDF(self):
        print(f'呼び出されました:{self.getKinmuDF.__name__}')
        return self.shiftCtrl.getKinmuForm(DataName.kinmu)

    def getYakinDF(self):
        print(f'呼び出されました:{self.getYakinDF.__name__}')
        return self.shiftCtrl.getYakinForm()
