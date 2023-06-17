import csv
import os
import config
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 夜勤・休日日勤の平均回数を求める n1:休日日勤可能技師数　n2:夜勤可能技師数
def calc_mean_of_night_and_daily(alpha, n1, n2):
    dailys = 0
    nights = 0
    for row in alpha[:4]:
        for i in row:
            dailys += i
    for row in alpha[4:7]:
        for i in row:
            nights += i
    return dailys/n1 + nights/n2

# 辞書の値からキーを抽出
def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None

def make_T(mydate, consectiveWork):
    Tdict = {}
    T = []; Tr = []; Tclosed = []; Topened = []; Toutput = []
    pre = mydate - timedelta(days = consectiveWork)
    post = mydate + relativedelta(months = 1)

    for d in range((post - pre).days + 1):
        strd = datetime.strftime(pre + timedelta(d), '%Y-%m-%d')
        Tdict[d] = strd
        T.append(d)

    pre = mydate
    post = post           
    for d in range((post - pre).days + 1):
        strd = datetime.strftime(pre + timedelta(d), '%Y-%m-%d')
        day = get_key_from_value(Tdict, strd)
        Toutput.append(day)
    
    pre = mydate
    post = post - timedelta(days=1)
    for d in range((post - pre).days + 1):
        strd = datetime.strftime(pre + timedelta(d), '%Y-%m-%d')
        day = get_key_from_value(Tdict, strd)
        Tr.append(day)
        holiday = JapanHoliday()
        if holiday.is_holiday(strd):
            Tclosed.append(day)
        else:
            Topened.append(day)


    return Tdict, T, Tr, Tclosed, Topened, Toutput

# 前月分の勤務，作成月分の希望勤務を再フォーマット
def reformat_F(F, Wdict, Tdict):
    d = []
    for arr in F:
        row = []
        row.append(arr[0])
        day = datetime.strptime(arr[1], '%Y/%m/%d')
        strd = datetime.strftime(day, '%Y-%m-%d')
        row.append(get_key_from_value(Tdict, strd))
        row.append(Wdict[arr[2]])   
        d.append(row)
    return d


# ダミー技師を作成　uidは900番台
def make_Ndum(num):
    Ndum = []
    number = 900
    for i in range(num):
        Ndum.append(number + i)

    return Ndum 
 
class JapanHoliday:
    """
    内閣府が公表している「平成29年（2017年）から平成31年（2019年）国民の祝日等
    （いわゆる振替休日等を含む）」のCSVを使用して
    入力された日付('2017-01-01' %Y-%m-%d形式)が土、日、休日か判定するクラス
    """
    
    def __init__(self, encoding='cp932'):
        dataDir = config.readSettingJson("DATA_DIR")
        _path = os.path.join(dataDir,'syukujitsu.csv')
        # _path = os.path.join(os.path.dirname(__file__), 'syukujitsu.csv')
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