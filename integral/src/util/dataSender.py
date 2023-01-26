import csv
import datetime
from enum import Enum, auto
import locale
import logging
import math
import os

import pandas as pd
from decorator.convertTable import ConvertTable


from database.member import Members
from util.dataReader import *


class DataName(Enum):
    kinmu = auto()
    request = auto()
    previous = auto()


class DataSender(Members):
    """
    できればmodelにはDFを当て込めたい
    その際、各DFで共通する部分を連動させないといけないので要注意
    """

    def __init__(self):
        super().__init__()

    def toHeader_fullspan(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.datetime.strftime(datetime.date(*yyyymmdd), '%Y-%m-%d') for yyyymmdd in self.day_previous_next]

    def toHeader_nowMonth(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.datetime.strftime(datetime.date(*yyyymmdd), '%Y-%m-%d') for yyyymmdd in self.now_month]
        
    def strDate4Access(self, date):

        return datetime.datetime.strftime(datetime.date(*date), '%Y/%m/%d')

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
        # df.at[strday, int(job)] is not None
        # math.isnan(df.at[strday, int(job)])
        df = pd.DataFrame(None, columns=[4, 5, 6, 0, 1, 2, 3, -3], index=self.toHeader_nowMonth())
        for person in self.members.values():
            for strday, job in zip(self.toHeader_nowMonth(), person.jobPerDay.values()):
                if job  in ["4", "5", "6", "0", "1", "2", "3"]:
                    if type(df.at[strday, int(job)]) is str and job == "3":
                        df.at[strday, -3] = person.name
                    else:
                        df.at[strday, int(job)] = person.name

        # print(df.loc[:"2023-04-05", [1, 2]])
        return df.where(df.notna(),'')


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
        df = pd.DataFrame(None, columns=self.toHeader_fullspan(), index=self.members.keys())
        if dataName == DataName.kinmu:
            
            #3月は空，4月～5月1日まで
            for uid, person in self.members.items():
                for day, job in person.jobPerDay.items():
                    strday :str = datetime.datetime.strftime(datetime.date(*day[:3]), '%Y-%m-%d')
                    if day >= (self.date.year, self.date.month, self.date.day):
                        df.at[uid, strday] = job
                    else :
                        df.at[uid, strday] = None
            
        if dataName == DataName.previous:
            for uid, person in self.members.items():
                for day, job in person.jobPerDay.items():
                    strday :str = datetime.datetime.strftime(datetime.date(*day[:3]), '%Y-%m-%d')
                    if day < (self.date.year, self.date.month, self.date.day):
                        df.at[uid, strday] = job
                    else :
                        df.at[uid, strday] = None


        elif dataName == DataName.request:
            
            df = pd.DataFrame(None, columns=self.toHeader_fullspan(), index=self.members.keys())
            for uid, person in self.members.items():
                for day, job in person.requestPerDay.items():
                    strday :str = datetime.datetime.strftime(datetime.date(*day[:3]), '%Y-%m-%d')
                    df.at[uid, strday] = job
                
            # df = pd.DataFrame({uid: person.requestPerDay for uid,
            #                   person in self.members.items()})

        # df.sort_index(axis=0, inplace=True)
        # logging.debug(df.T)
        staffDF:pd.DataFrame = self.getStaffInfo()
        order = staffDF.index.values.tolist()
        df = df.reindex(index=order)
        # self.shiftdf = self.shiftdf.reindex(index=order)

        return df.where(df.notna(),None)


    def getStaffInfo(self) -> pd.DataFrame:
        """
            UID 職員ID name depf(モダリティ)
        UID *value
        """
        df = pd.DataFrame({uid: {'uid':uid , '職員番号':person.staffid, '名前': person.name,'モダリティ': person.dept} for uid, person, in self.members.items()}).T
        logging.debug(df)
                # staffinfoをdeptでソートする
        sort_order = ['RT', 'MR', 'TV', 'KS', 'NM', 'XP', 'MG', 'MT', 'CT', 'XO', 'AG', 'FR', 'NF', 'AS', 'ET', '']
        # 任意列を分類カテゴリが入っているカラムにする
        # df = df.sort_values(by = ['uid'], ascending=True)
        df['モダリティ'] = pd.Categorical(df['モダリティ'], categories=sort_order)
        df = df.sort_values(by=['モダリティ', 'uid'], ascending=[True, True])
        return df

    # 日付の配列の中で休みを返す
    def getJapanHolidayDF(self):
        holidayHandler = JapanHoliday()
        holiday = []
        for day in self.toHeader_fullspan():
            if holidayHandler.is_holiday(day):
                holiday.append(day)
        return holiday

    def getCalendarDF(self):

        WEEKDAY = ['月','火','水','木','金','土','日']
        df = pd.DataFrame.from_dict(
            {
            'holiday':[0 for i in range(len(self.toHeader_fullspan()))],
            'date': [yyyymmdd[2] for yyyymmdd in self.day_previous_next],
            'weekday':[WEEKDAY[calendar.weekday(*yyyymmdd)] for yyyymmdd in self.day_previous_next],
            },
            orient = 'index',
            columns = self.toHeader_fullspan(),
        )

        return df

    def getDf4Iwasaki(self):
        pass

    
    def getAccessData(self):
        data = []
        for uid, person in self.members.items():
            for date in self.now_next_month:
                if (    date not in person.requestPerDay.keys() 
                    and (person.jobPerDay[date] != '8' and person.jobPerDay[date] is not None)
                    and uid < 900):
                    job = ConvertTable.convertTable[person.jobPerDay[date]]
                    line = [uid, self.strDate4Access(date), job]

                    data.append(line) 

        return data