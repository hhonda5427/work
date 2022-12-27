import os, csv
import config
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict


class DataModel():
    def __init__(self):
        # 設定値の読み込み
        configvar = self.readconfigvar()
        date = datetime.strptime(configvar['date'][0], '%Y/%m/%d')
        iota = int(configvar['iota'][0])
        Tdict, T, Tr, closed = self.createCalendar(date, iota)
        # 日付用のヘッダーデータの作成
        self.yyyymm = configvar['date'][0]
        self.closed = closed
        self.alpha = self.readalpha(Tr)
        self.header = self.createHeader(T, Tr, self.alpha)

        # 勤務表データの作成
        uid = self.getuid()
        self.shiftdf = pd.DataFrame(data=[['' for j in range(len(T))] for i in range(len(uid))], index=uid, columns=T)
        self.previousdf = pd.DataFrame(data=[[None for j in range(len(T))] for i in range(len(uid))], index=uid, columns=T)
        self.requestdf = pd.DataFrame(data=[[None for j in range(len(T))] for i in range(len(uid))], index=uid, columns=T)
        # self.prevreqdf = pd.DataFrame(data=[[None for j in range(len(T))] for i in range(len(uid))], index=uid, columns=T)
        shiftdata = self.readshift(os.path.join(config.DATA_DIR, 'data', 'shift.dat'), Tdict)
        previousdata = self.readshift(os.path.join(config.DATA_DIR, 'data', 'previous.dat'), Tdict)
        requestdata = self.readshift(os.path.join(config.DATA_DIR, 'data', 'request.dat'), Tdict)
        
        self.convertShift(self.shiftdf, shiftdata, T)
        self.convertShift(self.previousdf, previousdata, T)
        self.convertShift(self.requestdf, requestdata, T)
        # self.convertShift(self.prevreqdf, requestdata, T)

        # スタッフ情報用のヘッダーデータの作成
        # dept順で配列を作成する
        self.staffinfo = self._sortData(df=self.createStaff(shiftdata), first_colname='dept', second_colname='id', sort_order=None)

        # 休日，連続勤務を数えるテーブル作成
        self.counttable = self.createCountTable(self.staffinfo)
 
        # staffinfoと同じ並び順で配列を作成する
        order = self.staffinfo.index.values.tolist()
        # 
        # 勤務表データをスタッフ情報と同じuid順に変更
        self.shiftdf = self.shiftdf.reindex(index=order)
        self.previousdf = self.previousdf.reindex(index=order)
        self.requestdf = self.requestdf.reindex(index=order)
        
        # 欠損値nanを''に置き換える
        self.previousdf = self.previousdf.where(self.previousdf.notna(),None)
        self.requestdf = self.requestdf.where(self.requestdf.notna(),None)
        self.shiftdf = self.shiftdf.where(self.shiftdf.notna(), None)

        
    # 勤務表のテーブルを作成
    def convertShift(self, table, shift, T):
        # shiftdfを行でループ
        # shift[index, uid, T, shift]
        for index, row in table.iterrows():
            # shiftから指定したuidの行のみを抽出
            personal = shift[shift['uid'] == index]
            # uidで抽出した各個人のシフトをsiftdf(2次元配列)に入れる
            for idx, line in personal.iterrows():                
                table.at[line[0], line[1] ] = line[2]
        return None

    # ダミーを加えたスタッフ一覧を作成 
    def createStaff(self, shift):
        staffinfo = self.readstaffinfo()
        # shift = self.readshift(self.Tdict)
        dept = self.readNrdeptcore()
        
        # staffinfoに所属の情報を加える
        dept = dept.iloc[:, 0:2]
        staffinfo = pd.merge(staffinfo, dept, how='left', on='uid')

        # staffinfoにダミーの情報を加える
        # shift.datからdummyだけ抽出する
        dummy = shift[shift['uid'] >= 900]  #ダミーだけに絞る
        dummy = dummy['uid']        #uidのみにする
        dummy = dummy[~dummy.duplicated()]  #重複をなくす

        for dum in dummy:
            name = 'dummy'+str(dum)
            d = [[dum, dum, name, '']]
            col_names = ['uid', 'id', 'staffname', 'dept']
            df = pd.DataFrame(d, columns=col_names)
            staffinfo = pd.concat([staffinfo, df], axis=0, ignore_index=True)
        # indexをuidに変更する
        indexes = {}
        for index, staff in staffinfo.iterrows():
            indexes[index] = staff[0]    
        staffinfo = staffinfo.rename(index=indexes)   

        return staffinfo
    
    def createCountTable(self, staffinfo):
        index = staffinfo.index.values.tolist()
        columns = ['dayoff', 'consecutivework']
        
        table = pd.DataFrame(data=[[0 for j in range(2)] for i in range(len(staffinfo))], index=index, columns=columns)

        return table

    #日付ヘッダーを作成 
    def createHeader(self, T, Tr, alpha):
        WEEKDAY = ['月','火','水','木','金','土','日']
        dayoff = pd.DataFrame(data=[[0 for i in range(len(T))]], index=['dayoff'], columns=T)
        days = pd.DataFrame(data=[[i[-2:] for i in T]], index=['date'], columns=T)
        weekdays = pd.DataFrame(data=[[WEEKDAY[datetime.strptime(i, '%Y-%m-%d').weekday()] for i in T]], index=['weekday'], columns=T)

        for t in Tr:
            if t in T:
                dayoff.at['dayoff', t] = alpha.at['do', t]

        return pd.concat([dayoff, days, weekdays], axis=0)
    
    # 連続勤務を考慮して12日前~翌月1日までを含めたカレンダーを作成
    def createCalendar(self, createdate, consectivework):
        Tdict = {}
        T = []; Tr = []; Tclosed = []
        holiday = JapanHoliday()
        pre = createdate - timedelta(days= consectivework)
        post = createdate + relativedelta(months = 1)
        
        for i in range((post-pre).days + 1):
            strdate = datetime.strftime(pre + timedelta(i), '%Y-%m-%d')
            Tdict[i- consectivework] = strdate
            T.append(strdate)
            if holiday.is_holiday(strdate):
                Tclosed.append(strdate)
        pre = createdate
        post = post - timedelta(days=1)
        for i in range((post -pre).days + 1):
            strdate = datetime.strftime(pre + timedelta(i), '%Y-%m-%d')
            Tr.append(strdate)

        return Tdict, T, Tr, Tclosed

    def getuid(self):
        path = os.path.join(config.DATA_DIR, 'data', 'shift.dat')
        shift = pd.read_csv(path, header=None, skiprows=1, names=['uid', 'date', 'shift'])
        uid = shift.drop_duplicates('uid')
        return uid['uid'].values

    def readstaffinfo(self):
        path = os.path.join(config.DATA_DIR, 'data', 'staffinfo.dat')
        result = pd.read_csv(path, header=None, names=['uid', 'id', 'staffname'])
        
        return result

    def readshift(self, path, Tdict):
        # path = os.path.join(config.DATA_DIR, 'data', 'shift.dat')
        shift = pd.read_csv(path, header=None, skiprows=1, names=['uid', 'date', 'shift'])
        shiftDict = self.readshiftDict()

        for index, row in shift.iterrows():    
            shift.at[index, 'date']= Tdict[row['date']]
            shift.at[index, 'shift'] = shiftDict[row['shift']] 
        return shift

    def readrequest(self):
        shiftDict = self.readshiftDict()
        path = os.path.join(config.DATA_DIR, 'data', 'request.dat')
        request = pd.read_csv(path, header=None, names=['uid', 'T', 'shift']) 
        
        for index, row in request.iterrows():
            request.at[index, 'shift'] = shiftDict[row['shift']]    #at[]で元の要素を選択して処理すると更新される

        return request
    
    def readprevious(self):
        shiftDict = self.readshiftDict()
        path = os.path.join(config.DATA_DIR, 'data', 'previous.dat')
        previous = pd.read_csv(path, header=None, names=['uid', 'T', 'shift']) 
        
        for index, row in previous.iterrows():
            previous.at[index, 'shift'] = shiftDict[row['shift']]    #at[]で元の要素を選択して処理すると更新される

        return previous        

    def readconfigvar(self):
        path = os.path.join(config.DATA_DIR, 'data', 'configvar.dat')
        data = []
        configvar = defaultdict(list)
        with open(path, encoding='utf-8_sig') as f:
            for line in f:
                line = line.strip()
                data.append(list(line.split(',')))
            for d in data:
                for val in d[1:]:
                    configvar[d[0]].append(val)
        return configvar
    
    def readNrdeptcore(self):
        path = os.path.join(config.DATA_DIR, 'data', 'Nrdeptcore.dat')
        names = ['uid', 'dept', 'rt', 'mr', 'tv', 'ks', 'nm', 'xp', 'ct', 'xo', 'ag', 'mg', 'mt']
        return pd.read_csv(path, header=None, names=names)
    
    def readalpha(self, T):
        path = os.path.join(config.DATA_DIR, 'data', 'alpha.dat')
        alpha = pd.read_csv(path, header=None, index_col=0)
        alpha.columns = T

        return alpha

    def readshiftDict(self):
        shiftDict = {}
        path = os.path.join(config.DATA_DIR, 'data', 'converttable.dat')
        shiftTbl = pd.read_csv(path, header=None)
        for index, row in shiftTbl.iterrows():
            shiftDict[row[1]] = row[0]
        
        return shiftDict
    
    # ソートする
    def sortData(self, df:pd.DataFrame, first_colname, second_colname, sort_order=None):
        # staffinfoをdeptでソートする
        if sort_order is None:
            sort_order = ['RT', 'MR', 'TV', 'KS', 'NM', 'XP', 'MG', 'MT', 'CT', 'XO', 'AG', 'FR', 'NF', 'AS', 'ET', '']
        
        # 任意列を分類カテゴリが入っているカラムにする

        df[second_colname] = pd.Categorical(df[second_colname])
        df = df.sort_values(by=[second_colname])

        df[first_colname] = pd.Categorical(df[first_colname], categories=sort_order)
        df = df.sort_values(by=[first_colname])

        return df
    def _sortData(self, df:pd.DataFrame, first_colname, second_colname, sort_order=None):
        # staffinfoをdeptでソートする
        sort_order = ['RT', 'MR', 'TV', 'KS', 'NM', 'XP', 'MG', 'MT', 'CT', 'XO', 'AG', 'FR', 'NF', 'AS', 'ET', '']
        # 任意列を分類カテゴリが入っているカラムにする
        df[first_colname] = pd.Categorical(df[first_colname], categories=sort_order)
        df = df.sort_values(by=[first_colname, second_colname], ascending=[True, True])

        return df


class JapanHoliday:
    """
    内閣府が公表している「平成29年（2017年）から平成31年（2019年）国民の祝日等
    （いわゆる振替休日等を含む）」のCSVを使用して
    入力された日付('2017-01-01' %Y-%m-%d形式)が土、日、休日か判定するクラス
    """
    
    def __init__(self, encoding='cp932'):
        _path = os.path.join(config.DATA_DIR ,'data','syukujitsu.csv')
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
                day = datetime.strptime(day_str, '%Y/%m/%d')
                day_str = datetime.strftime(day, '%Y-%m-%d')
                holidays[day_str] = {'day': day_str, 'name': name}

        for y in range(datetime.today().year -3, datetime.today().year +3):
            for arr in tokai_holidays:
                day = datetime.strptime(str(y) + '-'+str(arr[0]), '%Y-%m-%d')
                day_str = datetime.strftime(day, '%Y-%m-%d')                     
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
            day = datetime.strptime(day_str, '%Y-%m-%d')
            week_num = self.get_weekNum(day)
            if day.weekday() >= 6 or (day.weekday() == 5 and (week_num == 2 or week_num == 4)):
                return True
        except ValueError:
            print('日付は2018-03-01 %Y-%m-%dの形式で入力してください')
            raise ValueError
        day = datetime.strptime(day_str, '%Y-%m-%d')
        day_str = datetime.strftime(day, '%Y-%m-%d')                     
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
    
    def get_weekNum(self, _date):
        divmod_=divmod(_date.day,7) #日付を7で割って商と余りを取得

        if divmod_[0] == 0:
            week_num = 1
        elif divmod_[1] == 0:
            week_num = divmod_[0]
        else:
            week_num = divmod_[0] + 1
        
        return week_num
