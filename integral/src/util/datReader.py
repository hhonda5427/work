import calendar
import datetime
import logging
from enum import Enum
from uuid import uuid4


from database.member import *
from decorator.convertTable import ConvertTable
from decorator.validate import *

logging.basicConfig(filename='PyQtPractice\log\data.log', level=logging.DEBUG)

# .datファイルを元に職員情報をもったオブジェクトを生成する


class DatNames(Enum):
    configvar = 'configvar.dat'
    staffinfo = 'staffinfo.dat'
    convertTable = 'converttable.dat'
    shift = 'shift.dat'
    request = 'request.dat'
    previous = 'previous.dat'
    Nrdeptcore = 'Nrdeptcore.dat'


class DatReader(Members):

    def __init__(self, rootPath: str):
        super().__init__()
        self.rootPath = rootPath
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
            inputData = open(self.rootPath + "\\" +
                             DatNames.configvar.value, 'r', encoding='utf-8-sig')

        data = {}
        for row in inputData:
            elem = row.rstrip('\n').split(',')
            data[elem[0]] = elem[1:]

        inputData.close()

        # 日付データを設定
        self.date: datetime.datetime = datetime.datetime.strptime(
            *data['date'], '%Y/%m/%d')
        cal = calendar.Calendar()
        self.previous_month = [datetuple for datetuple in cal.itermonthdays4(
            self.date.year, self.date.month-1) if datetuple[1] == self.date.month - 1]
        self.now_month = [datetuple for datetuple in cal.itermonthdays4(
            self.date.year, self.date.month) if datetuple[1] == self.date.month]
        self.next_month = [datetuple for datetuple in cal.itermonthdays4(
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
            inputData = open(self.rootPath + "\\" +
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

        return self

    def dat2Member(self, readDatName: DatNames, month_calendar: list[tuple[int, int, int, int]], datPath=''):
        try:
            readingDat = open(datPath, 'r', encoding='utf-8-sig')
        except FileNotFoundError as ex:
            readingDat = open(self.rootPath + "\\" +
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
                    '*.datのdayがカレンダーと一致しませんでした。\n詳細: {ex}\nスキップして次を読み込みます...')
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
            inputData = open(self.rootPath + "\\" +
                             DatNames.Nrdeptcore.value, 'r', encoding='utf-8-sig')

        for row in inputData:
            elem = row.rstrip('\n').split(',')
            self.members[int(elem[0])].dept = elem[1]

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
            inputData = open(self.rootPath + "\\" +
                             DatNames.convertTable.value, 'r', encoding='utf-8-sig')

        for row in inputData:
            try:
                name, num = row.rstrip('\n').split(',')
                ConvertTable.convertTable[num] = name #後の変換を楽にするためにあえてnumをkeyに
            except ValueError as ex:
                print(f'異常なデータがありました\n詳細: {ex}\nスキップして次を読み込みます...')
                continue
