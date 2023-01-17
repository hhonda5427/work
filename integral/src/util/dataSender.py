import csv
import datetime
from enum import Enum, auto
import locale
import logging
import os

import pandas as pd
from decorator.convertTable import ConvertTable


from database.member import Members


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

    def toDateHeader(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.datetime.strftime(datetime.date(*yyyymmddww[:3]), '%Y-%m-%d') for yyyymmddww in self.day_previous_next]

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
        df = pd.DataFrame(None, columns=self.toDateHeader(), index=self.members.keys())
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
            
            df = pd.DataFrame(None, columns=self.toDateHeader(), index=self.members.keys())
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

    def getJapanHolidayDF(self):
        holidayHandler = JapanHoliday()
        holiday = []
        for day in self.toDateHeader():
            if holidayHandler.is_holiday(day):
                holiday.append(day)
        return holiday

    def getDf4Iwasaki(self):
        pass



class JapanHoliday:
    """
    内閣府が公表している「平成29年（2017年）から平成31年（2019年）国民の祝日等
    （いわゆる振替休日等を含む）」のCSVを使用して
    入力された日付('2017-01-01' %Y-%m-%d形式)が土、日、休日か判定するクラス
    """
    
    def __init__(self, encoding='cp932'):
        _path = os.path.join("integral\data\syukujitsu.csv",'syukujitsu.csv')
        self._holidays = self._read_holiday(_path, encoding)
 
    def _read_holiday(self, path, encoding):
        """
        CSVファイルを読み込み、self.holidaysに以下の形式のdictをListに格納する
        {'2017-01-09': {'day': '2017-01-09', 'name': '成人の日'}}
        CSVファイルがないとIOErrorが発生する
 
        :param path: 祝日と祝日名が記入されたCSVファイル。ヘッダーが必要
        :param encoding: CSVファイルのエンコーディング
        :return: [{'2017-01-09': {'day': '2017-01-09', 'name': '成人の日'}...}]
        """
        holidays = {}
        tokai_holidays = [['01-02','東海大休日'],['01-03','東海大休日'],['11-01','建学の日'],
                          ['12-29','東海大休日'],['12-30','東海大休日'],['12-31','東海大休日']]
        with open(path, encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            next(reader)  # CSVのヘッダーを飛ばす
            for row in reader:
                day_str, name = row[0], row[1]
                day = datetime.datetime.strptime(day_str, '%Y/%m/%d')
                day_str = datetime.datetime.strftime(day, '%Y-%m-%d')
                holidays[day_str] = {'day': day_str, 'name': name}

        for y in range(datetime.datetime.today().year -3, datetime.datetime.today().year +3):
            for arr in tokai_holidays:
                day = datetime.datetime.strptime(str(y) + '-'+str(arr[0]), '%Y-%m-%d')
                day_str = datetime.datetime.strftime(day, '%Y-%m-%d')                     
                holidays[day_str] = {'day': day_str, 'name':arr[1]}
        return holidays
        
    def is_holiday(self, day_str):
        """
        土、日、祝日か判定する
        :param day_str: '2018-03-01'の%Y-%m-%dのstrを受け取る。
                        形式が違うとValueErrorが発生
        :return: 土、日、祝日ならTrue, 平日ならFalse
        """
        try:
            day = datetime.datetime.strptime(day_str, '%Y-%m-%d')
            week_num = self.get_weekNum(day)
            if day.weekday() >= 6 or (day.weekday() == 5 and (week_num == 2 or week_num == 4)):
                return True
        except ValueError:
            print('日付は2018-03-01 %Y-%m-%dの形式で入力してください')
            raise ValueError
        day = datetime.datetime.strptime(day_str, '%Y-%m-%d')
        day_str = datetime.datetime.strftime(day, '%Y-%m-%d')                     
        if day_str in self._holidays:
            return True
        return False
 
    def get_holiday_dict(self):
        """
        祝日を一覧化したdictを返す
        {'2017-01-09': {'day': '2017-01-09', 'name': '成人の日'},
         '2017-02-11': {'day': '2017-02-11', 'name': '建国記念の日'},...}
        """
        return self._holidays
    
    def get_weekNum(self, _date:datetime.datetime):
        divmod_=divmod(_date.day,7) #日付を7で割って商と余りを取得

        if divmod_[0] == 0:
            week_num = 1
        elif divmod_[1] == 0:
            week_num = divmod_[0]
        else:
            week_num = divmod_[0] + 1
        
        return week_num