import calendar
import csv
import datetime
import logging
from enum import Enum
import os
import pathlib
from uuid import uuid4


from database.member import *
from decorator.convertTable import ConvertTable
from decorator.validate import *
from settings.settings import *
# logging.basicConfig(filename='PyQtPractice\log\data.log', level=logging.DEBUG)

# .datファイルを元に職員情報をもったオブジェクトを生成する


class DatNames(Enum):
    configvar = 'configvar.dat'
    staffinfo = 'staffinfo.dat'
    convertTable = 'converttable.dat'
    shift = 'shift.dat'
    request = 'request.dat'
    previous = 'previous.dat'
    Nrdeptcore = 'Nrdeptcore.dat'
    skill = 'skill.dat'
    


class DataReader(Members):

    def __init__(self) :
        super().__init__()
        self.rootPath = pathlib.Path(ROOT_PATH)
        self.readConfigvar()
        self.readStaffInfo()
        self.applyShift2Member()
        self.readNrdeptcore()
        self.readConvertTable()

    def readConfigvar(self, datPath: str = ''):
        """次のようなデータ構造を想定しています
        date,2023/04/01
        kappa,150
        iota,12
        myu,8
        nyu,3,0,0
        rho,3
        epsilon,5
        lambda,0.1,0.01,0.01,0.001,0.1
        """
        try:
            inputData = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            inputData = open(self.rootPath/ 
                             DatNames.configvar.value, 'r', encoding='utf-8-sig')

        data = {}
        for row in inputData:
            elem = row.rstrip('\n').split(',')
            data[elem[0]] = elem[1:]
        self.config = data

        inputData.close()

        # 日付データを設定
        self.date: datetime.datetime = datetime.datetime.strptime(
            *data['date'], '%Y/%m/%d')
        
        cal = calendar.Calendar()
        self.previous_month = [datetuple for datetuple in cal.itermonthdays3(
            self.date.year, self.date.month-1) if datetuple[1] == self.date.month - 1][-int(data['iota'][0]):]
        self.now_month = [datetuple for datetuple in cal.itermonthdays3(
            self.date.year, self.date.month) if datetuple[1] == self.date.month]
        self.next_month = [datetuple for datetuple in cal.itermonthdays3(
            self.date.year, self.date.month+1) if datetuple[1] == self.date.month + 1]

        self.now_next_month = self.now_month + [self.next_month[0]]
        
        self.day_previous_next = self.previous_month + \
            self.now_month + [self.next_month[0]]

    def readStaffInfo(self, datPath: str = ''):
        """次のようなデータ構造を想定しています
        uid, staffid, name
        2,R04793,小川智
        4,055236,戸高秀晴
        5,059247,福井浩
        6,067607,佐藤雄喜
        7,076610,川嶋康裕
        8,078321,池田秀
        9,090668,笠原賢治
        10,090670,高橋直紀
        11,109876,平田聡
        """
        try:
            inputData = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            inputData = open(self.rootPath/ 
                             DatNames.staffinfo.value, 'r', encoding='utf-8-sig')

        for row in inputData:
            try:
                uid, staffid, name = row.rstrip('\n').split(',')
                self.members[int(uid)] = Person(staffid, name)
            except ValueError as ex:
                print(f'異常なデータがありました\n詳細: {ex}\nスキップして次を読み込みます...')
                continue

        inputData.close()

    # 先月分とrequestは一括読み込みして、一部分だけほしいときは切り取るやり方にします
    @Validater.validJobPerDay
    def applyShift2Member(self, shiftPath: str = '', previousPath: str = '', requestPath: str = ''):
        """次のようなデータ構造を想定しています
        uid, day, job
        2,0,63
        2,1,10
        2,2,8
        2,3,8
        2,4,8
        2,5,8
        2,6,8
        """

        self.dat2Member(DatNames.shift, self.now_next_month)
        self.dat2Member(DatNames.previous, self.previous_month)
        self.dat2Member(DatNames.request, self.now_next_month)
        # print(self.day_previous_next )


        # self.day_previous_next = self.day_previous_next[self.day_previous_next.index((self.date.year, self.date.month, self.date.day, self.date.weekday()))-mindate-1:]


        return self

    def dat2Member(self, readDatName: DatNames, month_calendar: list[tuple[int, int, int, int]], datPath=''):
        try:
            readingDat = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            readingDat = open(self.rootPath/ 
                              readDatName.value, 'r', encoding='utf-8-sig')

        for row in readingDat:
            
            try:
                uid, day, job = row.rstrip('\n').split(',')
                # ここで得たdayは(yyyy, mm, dd, ww)に変換
                # dayの'-（マイナス）'データはindex指定として扱えば上手くいくはず
                date = month_calendar[int(day)]

                if not date in self.day_previous_next:
                    raise damagedDataError

            except damagedDataError as ex:
                print(
                    f'*.datのdayがカレンダーと一致しませんでした。\n詳細: {ex}\nスキップして次を読み込みます...')
                continue
            except IndexError as ex:
                print(f'{ex}\n{readDatName}\n {int(day)}')

            except ValueError as ex:
                print(f'異常なデータがありました\n詳細: {ex}\nスキップして次を読み込みます...')
                continue

            if readDatName == DatNames.shift or readDatName == DatNames.previous:
                try:
                    self.members[int(uid)].jobPerDay[date] = job
                except KeyError as ex:
                    self.members[int(uid)] = Person(uuid4(), f'dummy{uid}')
                    self.members[int(uid)].jobPerDay[date] = job
            elif readDatName == DatNames.request:
                try:
                    self.members[int(uid)].requestPerDay[date] = job
                except KeyError as ex:
                    self.members[int(uid)] = Person(uuid4(), f'dummy{uid}')
                    self.members[int(uid)].requestPerDay[date] = job

        readingDat.close()
        
    def readSkill(self, datPath = ''):
        """
        uid, aN, mN, cN... 
        2,0,0,0,0,0,0
        4,0,0,0,0,0,0
        98,0,0,0,0,0,0
        97,0,0,0,2,0,2
        96,0,0,0,0,0,0
        5,0,0,0,0,0,0
        6,0,0,2,2,0,2
        7,0,0,0,0,0,
        """
        try:
            inputData = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            inputData = open(self.rootPath/ 
                             DatNames.skill.value, 'r', encoding='utf-8-sig')

        for row in inputData:
            elem = row.rstrip('\n').split(',')
            self.members[int(elem[0])].skill = elem[1:]
        inputData.close()


            
    def readNrdeptcore(self, datPath: str = ''):
        """
        次のようなデータ構造を想定しています
        uid, dept
        2,MR,0,2,1,2,0,0,0,2,0,0,0
        4,RT,6,0,0,0,0,0,0,0,0,0,0
        98,KS,0,0,0,2,0,0,0,0,0,0,0
        97,XO,0,0,0,0,0,0,0,2,0,0,0
        96,AG,0,0,0,0,0,0,0,0,2,0,0
        5,FR,2,0,1,2,0,1,0,2,0,0,0
        6,XP,0,0,0,0,0,6,6,2,0,0,0
        7,AG,0,0,0,0,0,0,0,2,6,0,0
        8,XO,0,0,0,0,0,1,6,6,0,0,0
        """
        try:
            inputData = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            inputData = open(self.rootPath/ 
                             DatNames.Nrdeptcore.value, 'r', encoding='utf-8-sig')

        for row in inputData:
            elem = row.rstrip('\n').split(',')
            self.members[int(elem[0])].dept = elem[1]
            self.members[int(elem[0])].modalityN = elem[2:]
        inputData.close()

    def readConvertTable(self, datPath: str = ''):
        """
        次のようなデータ構造を想定しています
        A日,0
        M日,1
        C日,2
        F日,3
        A夜,4
        M夜,5
        C夜,6
        """
        try:
            inputData = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            inputData = open(self.rootPath/ 
                             DatNames.convertTable.value, 'r', encoding='utf-8-sig')

        for row in inputData:
            try:
                name, num = row.rstrip('\n').split(',')
                ConvertTable.convertTable[num] = name #後の変換を楽にするためにあえてnumをkeyに
            except ValueError as ex:
                print(f'異常なデータがありました\n詳細: {ex}\nスキップして次を読み込みます...')
                continue


class JapanHoliday():
    """
    内閣府が公表している「平成29年（2017年）から平成31年（2019年）国民の祝日等
    （いわゆる振替休日等を含む）」のCSVを使用して
    入力された日付('2017-01-01' %Y-%m-%d形式)が土、日、休日か判定するクラス
    """
    
    def __init__(self, encoding='cp932'):
        _path = os.path.join(ROOT_PATH,'syukujitsu.csv')
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
