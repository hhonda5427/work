import datetime
from enum import Enum, auto
import locale
import logging

import pandas as pd
from decorator.convertTable import ConvertTable


from database.member import Members


class DataName(Enum):
    kinmu = auto()
    request = auto()


class DataSender(Members):
    """
    できればmodelにはDFを当て込めたい
    その際、各DFで共通する部分を連動させないといけないので要注意
    """

    def __init__(self):
        super().__init__()

    def toHeader(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.date(*yyyymmddww[:3]).strftime('%x')+datetime.date(*yyyymmddww[:3]).strftime('%a')
                for yyyymmddww in self.day_previous_next]

    def getDf4Shimizu(self):

        pass
    """
    ed, 最終日
    dfshift, getKinmuForm(DataName.kinmu)でおそらくOK
    data_list 多分日付のリスト
    
    DFyakinhyou, 夜勤表
             4           5,        6,        0,         1,          2,        3,         30
        "Angio夜勤", "MRI夜勤", "CT夜勤","Angio日勤", "MRI日勤", "CT日勤", "Free日勤", "Free日勤"
    
    日付 *uid
    
    """

    def getYakinForm(self) -> pd.DataFrame:
        yakinUnion = {'4', '5', '6', '0', '1', '2', '3', '30'}
        yakinTemp = {day: {job: uid} for uid, person in self.members.items()
                     for day, job in person.jobPerDay.items() if job in yakinUnion}

        df = pd.DataFrame(yakinTemp)
        df.where(pd.notnull(df), None, inplace=True)#whereじゃなくreplaceでうまくいくかも
        df.sort_index(axis=1, inplace=True)
        logging.debug(df.T)
        return df.T

    # 本田さん向け
    @ConvertTable.id2Name
    def getKinmuForm(self, dataName: DataName) -> pd.DataFrame:
        """ 
        DataName.kinmu           
            日付-veriant  日付 (yyyy-mm-dd)  日付+1
        UID *勤務(Not int)
            *無いときはNone

        DataName.request
            日付-veriant  日付               日付+1
        UID *request(Not int)  request
            *無いときはNone

        """
        if dataName == DataName.kinmu:
            df = pd.DataFrame({uid: person.jobPerDay for uid,
                              person in self.members.items()})
        elif dataName == DataName.request:
            df = pd.DataFrame({uid: person.requestPerDay for uid,
                              person in self.members.items()})

        df.sort_index(axis=0, inplace=True)
        # logging.debug(df.T)
        return df.T


    def getStaffInfo(self) -> pd.DataFrame:
        """
            UID 職員ID name depf(モダリティ)
        UID *value
        """
        df = pd.DataFrame({uid: {'uid': uid, 'staffID': person.staffid, '名前': person.name,
                          'モダリティ': person.dept} for uid, person, in self.members.items()})
        logging.debug(df.T)
        return df.T

    def getDf4Iwasaki(self):
        pass
