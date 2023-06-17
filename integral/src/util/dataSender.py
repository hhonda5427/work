import datetime
from enum import Enum, auto
import locale
import logging

import pyodbc
import pandas as pd
from decorator.convertTable import *


from util.dataReader import *

class DataName(Enum):
    kinmu = auto()
    request = auto()
    previous = auto()
    DFNrdept = auto()
    RawDFNrdeptcore = auto()
    DFCore = auto()


class DataSender(DataReader):

    def __init__(self):
        super().__init__()
        self.rk = int(self.config['iota'][0])
        self.kinmu_full = None 
    # getYakinForm_uidの戻り値であるdataframeの要素を、uidからnameに変換するデコレータ
    def uid2name(func):
        def wrapper(self, *args, **kwargs):
            df:pd.DataFrame = func(self, *args, **kwargs)
            #ここでうけとるdfは、getYakinForm_uidの戻り値
            for uid, person in self.members.items():
                df = df.replace(uid, person.name)
            return df
        return wrapper


    def toHeader_fullspan(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.datetime.strftime(datetime.date(*yyyymmdd), '%Y-%m-%d') for yyyymmdd in self.day_previous_next]

    def toHeader_previous(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.datetime.strftime(datetime.date(*yyyymmdd), '%Y-%m-%d') for yyyymmdd in self.previous_month]

    def toHeader_now_next(self) -> list[str]:
        locale.setlocale(locale.LC_TIME, 'ja_JP')
        return [datetime.datetime.strftime(datetime.date(*yyyymmdd), '%Y-%m-%d') for yyyymmdd in self.now_next_month]
    
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
    # getYakinFormの、dataframeの値にuidをいれるver
    # @Debugger.toCSV
    def getYakinForm_uid(self) -> pd.DataFrame:
        df = pd.DataFrame(None, columns=[4, 5, 6, 0, 1, 2, 3, -3], index=self.toHeader_nowMonth())
        for uid, person in self.members.items():
            for strday, job in zip(self.toHeader_nowMonth(), person.jobPerDay.values()):
                if job  in ["4", "5", "6", "0", "1", "2", "3"]:
                    if pd.notnull(df.at[strday, 3]) and job == "3":
                    # if df.at[strday, 3].notnull() and job == "3":
                        df.at[strday, -3] = uid 
                    else:
                        df.at[strday, int(job)] = uid
        df = df.rename(columns={4:'A夜', 5:'M夜', 6:'C夜', 0:'A日', 1:'M日', 2:'C日', 3:'F日1', -3:'F日2'})
        return df.where(df.notna(),'')
    
    #↓発展的！
    #uid2nameデコレータは、起動時に実行される。
    #つまり、getYakinFormはクラスメソッドではなく、インスタンスメソッドになる。
    #何が言いたいかというと、getYakinFormはdatファイルを読み込んだインスタンスの情報を参照するということ
    getYakinForm = uid2name(getYakinForm_uid)
    
    #jobPerDayとrequestPerDayを比較して、その日のJobが希望の場合は、trueを日付のvalueとする
    def getReqestMatch(self) -> pd.DataFrame:
        df = pd.DataFrame(None, columns=[4, 5, 6, 0, 1, 2, 3, -3], index=self.toHeader_nowMonth())
        for uid, person in self.members.items():
            for strday, day_and_job in zip(self.toHeader_nowMonth(), person.jobPerDay.items()):
                if day_and_job[1]  in ["4", "5", "6", "0", "1", "2", "3"]:
                    if pd.notnull(df.at[strday, 3]) and day_and_job[1] == "3":
                        # strdayがperson.requestPerDayのkeyに含まれている場合、df.at[strday, -3] = True
                        if strday in person.requestPerDay.keys():
                            df.at[strday, -3] = True
                        else:
                            df.at[strday, -3] = False
                        
                    else:
                        # strdayがperson.requestPerDayのkeyに含まれている場合、df.at[strday, -3] = True
                        if day_and_job[0] in person.requestPerDay.keys():
                            df.at[strday, int(day_and_job[1])] = True
                        else:
                            df.at[strday, int(day_and_job[1])] = False
        df = df.rename(columns={4:'A夜', 5:'M夜', 6:'C夜', 0:'A日', 1:'M日', 2:'C日', 3:'F日1', -3:'F日2'})
        return df.where(df.notna(),'')



    
    

#####後々実装予定？requestPerDayは、jobPerDayと同じ形式であることが前提######
#    # getYakinFormの、jobPerDayではなくrequestPerDayを参照するver
#    def getYakinForm_request(self) -> pd.DataFrame:
#        df = pd.DataFrame(None, columns=[4, 5, 6, 0, 1, 2, 3, -3], index=self.toHeader_nowMonth())
#        for uid, person in self.members.items():
#            for strday, job in zip(self.toHeader_nowMonth(), person.requestPerDay.values()):
#                if job  in ["4", "5", "6", "0", "1", "2", "3"]:
#                    if pd.notnull(df.at[strday, 3]) and job == "3":
#                        df.at[strday, -3] = uid 
#                    else:
#                        df.at[strday, int(job)] = uid
#                # 
#        df = df.rename(columns={4:'A夜', 5:'M夜', 6:'C夜', 0:'A日', 1:'M日', 2:'C日', 3:'F日1', -3:'F日2'})
#        return df.where(df.notna(),'')
    
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
        df = df.sort_values(by=['モダリティ', '職員番号'], ascending=[True, True])
        df = df.drop(columns=['uid', '職員番号'])
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

    # @Debugger.toCSV   
    def getDFstaff(self):
        uidL, staffidL, nameL = [], [], []
        for uid, person in self.members.items():
            uidL.append(uid)
            staffidL.append(person.staffid)
            nameL.append(person.name)
        unsorted = pd.DataFrame({'No':uidL, 'ID':staffidL, 'Name':nameL})
        return unsorted.sort_values(by=['No'], ascending=[True])

    # @Debugger.toCSV
    def getNrdeptcore(self, dataName: DataName):
        uidL, deptL, rtL, mrL, tvL, ksL, nmL, xpL, ctL, xoL, agL, mgL, mtL=\
            [], [], [], [], [], [], [], [], [], [], [], [], []  


        for uid, person in self.members.items():
            if uid >= 900:
                continue            
            uidL.append(uid)
            deptL.append(person.dept)
            rtL.append(person.modalityN[0])
            mrL.append(person.modalityN[1])
            tvL.append(person.modalityN[2])
            ksL.append(person.modalityN[3])
            nmL.append(person.modalityN[4])
            xpL.append(person.modalityN[5])
            ctL.append(person.modalityN[6])
            xoL.append(person.modalityN[7])
            agL.append(person.modalityN[8])
            mgL.append(person.modalityN[9])
            mtL.append(person.modalityN[10])
        d = {'Mo':deptL, \
            'RT':rtL, 'MR':mrL, 'TV':tvL, 'KS':ksL, 'NM':nmL ,\
            'XP':xpL, 'CT':ctL, 'XO':xoL, 'AG':agL, 'MG':mgL, 'MT':mtL}
        baseDF = pd.DataFrame(data=d, index=uidL)
        # pd.DataFrame({'UID':uidL, 'Mo':deptL, \
        #     'RT':rtL, 'MR':mrL, 'TV':tvL, 'KS':ksL, 'NM':nmL ,\
        #     'XP':xpL, 'CT':ctL, 'XO':xoL, 'AG':agL, 'MG':mgL, 'MT':mtL})    
        
        if dataName == DataName.DFNrdept:
            return baseDF['Mo']
        elif dataName == DataName.RawDFNrdeptcore:
            return baseDF
        elif dataName == DataName.DFCore:
            coreDict = {}
            coreDict['DFRTCore'] = baseDF.query('Mo=="RT" & RT=="6"').index.values.tolist()
            coreDict['DFMRCore'] = baseDF.query('Mo=="MR" & MR=="6"').index.values.tolist()
            coreDict['DFTVCore'] = baseDF.query('Mo=="TV" & TV=="6"').index.values.tolist()
            coreDict['DFKSCore'] = baseDF.query('Mo=="KS" & KS=="6"').index.values.tolist()
            coreDict['DFNMCore'] = baseDF.query('Mo=="NM" & NM=="6"').index.values.tolist()
            coreDict['DFXPCore'] = baseDF.query('Mo=="XP" & XP=="6"').index.values.tolist()
            coreDict['DFCTCore'] = baseDF.query('Mo=="CT" & CT=="6"').index.values.tolist()
            coreDict['DFXOCore'] = baseDF.query('Mo=="XO" & XO=="6"').index.values.tolist()
            coreDict['DFAGCore'] = baseDF.query('Mo=="AG" & AG=="6"').index.values.tolist()
            coreDict['DFMGCore'] = baseDF.query('Mo=="MG" & MG=="6"').index.values.tolist()
            coreDict['DFMTCore'] = baseDF.query('Mo=="MT" & MT=="6"').index.values.tolist()
            
            return coreDict
        else:
            pass

    # @Debugger.toCSV
    def getDFSkill(self):
        uidL, agNightL, mrNightL, ctNightL, fDayL, nightL, dayL = \
            [], [], [], [], [], [], []
        for uid, person in self.members.items():

            if uid >= 900:
                continue
            uidL.append(uid)
            agNightL.append(person.skill[0])
            mrNightL.append(person.skill[1])
            ctNightL.append(person.skill[2])
            fDayL.append(person.skill[3])
            nightL.append(person.skill[4])
            dayL.append(person.skill[5])

        d = {'A夜':agNightL, 'M夜':mrNightL, 'C夜':ctNightL, 'F':fDayL, '夜勤':nightL, '日勤':dayL}
        return pd.DataFrame(data=d, index=uidL)

    @ConvertTable.id2Name
    def getDFKinmuOnly(self):
        df = pd.DataFrame(None, columns=self.toHeader_now_next(), index=self.members.keys())
        for uid, person in self.members.items():
                for day, job in person.jobPerDay.items():
                    strday :str = datetime.datetime.strftime(datetime.date(*day), '%Y-%m-%d')
                    if day >= (self.date.year, self.date.month, self.date.day):
                        df.at[uid, strday] = job
        return df
 
    @ConvertTable.id2Name
    def getDFPreviousOnly(self):
        df = pd.DataFrame(None, columns=self.toHeader_previous(), index=self.members.keys())
        for uid, person in self.members.items():
                for day, job in person.jobPerDay.items():
                    strday :str = datetime.datetime.strftime(datetime.date(*day), '%Y-%m-%d')
                    if day < (self.date.year, self.date.month, self.date.day):
                        df.at[uid, strday] = job
        return df

    # @Debugger.toCSV
    def getDFKinmuFull(self):
        previous = self.getDFPreviousOnly()
        now_next = self.getDFKinmuOnly()

        self.kinmu_full = pd.concat([previous, now_next], axis=1)
        return self.kinmu_full 

    # @Debugger.toCSV   
    def getDFRenzoku(self):
        try:
            if df == None:
                raise damagedDataError
            df = self.kinmu_full
        except damagedDataError:
            df = self.getDFKinmuFull()
        except NameError as ex:
            df = self.getDFKinmuFull()
        except AttributeError as ex:
            df = self.getDFKinmuFull()
        offList = ['休', '夏', '振', '特', '年', '暇']
        workList = ['A日', 'M日', 'C日', 'F日', 'A夜', 'M夜', 'C夜', '明', '勤', '張', \
                    'MR', 'TV', 'KS', 'NM', 'AG', 'RT', 'XP', 'CT', 'XO', 'FR', 'NF', \
                    'MG', 'MT', 'AS', 'ET', '援', '他','半', 'ダ']
        df.replace(offList, None, inplace=True)
        df.replace(workList, '1', inplace=True)


        # df.replace(['明', '張', '援', '他' ,'休', '振' ,'夏', '特' ,'年', '暇'], None, inplace=True)
        # df.replace(['A日', 'M日', 'C日','A夜','M夜','C夜','勤','半','ダ'], 1, inplace=True)
        
        df.columns = [i - self.rk for i in range(len(self.day_previous_next))]
        df.index = [uid for uid in self.members.keys()]
        # # renzokuDF = pd.DataFrame(columns=[i-self.rk for i in range(len(self.day_previous_next))],\
        #      index=list(self.members.keys()))
        # for uid, person in self.members.items():
        #     for i, job in enumerate(person.jobPerDay.values()):
        #         if job in ["7", "9", "40", "41", "10", "50", "11", "60", "61", "63"]:
        #             renzokuDF.at[uid, i - self.rk] = None                    
        #         else:
        #             renzokuDF.at[uid, i - self.rk] = 1                    
        return df 

    # @Debugger.toCSV
    def getDFShift(self):
        uidL, dateL, jobL = [], [], []

        for uid, person in self.members.items():
            for day, job in person.jobPerDay.items():
                if day >= (self.date.year, self.date.month, self.date.day) and day < self.next_month[0]:
                    uidL.append(uid)
                    dateL.append(int(day[2])-1)
                    jobL.append(job)
        d = {'Date': dateL, 'Job':jobL}
        return pd.DataFrame(data=d, index=uidL)
    #    return pd.DataFrame({'UID': uidL, 'Date': dateL, 'Job':jobL}) 
        
    def getAccessData(self, isRequestOnly=False) -> list:
        data = []
        holidays = self.getJapanHolidayDF()
        for uid, person in self.members.items():
            for date in self.now_next_month:
                if ((person.jobPerDay[date] != '8' and person.jobPerDay[date] is not None)  #該当する日付の勤務が'勤'でなく，かつNoneでない->日勤はデータベースへ値を送らない
                    and uid < 900):
                    # job = ConvertTable.convertTable[person.jobPerDay[date]]
                    if date in person.requestPerDay.keys():
                        job = ConvertTable.convertTable[person.requestPerDay[date]]

                    else:
                        if isRequestOnly:
                            job = ""
                        else:
                            job = ConvertTable.convertTable[person.jobPerDay[date]]
                    line = [uid, self.strDate4Access(date), job]
                    
                    data.append(line) 

        return data

    def send2accdb(self, isRequestOnly=False):
        database_path = readSettingJson('DATABASE_PATH')
        # [uid, workdate, shift]
        records = self.getAccessData(isRequestOnly)


        conn_str = (
            r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            f'DBQ={database_path};'
            r'PWD=0000;'
        )
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        for record in records:
            uid = record[0]
            workdate = record[1]
            job = record[2]
            updating = datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d %H:%M:%S')
            operator = "admin"
            
            sql = (
                f"SELECT count(*) "
                f"FROM tblShift "
                f"WHERE uid = {uid} AND workdate =#{workdate}#"
                )
            cursor.execute(sql)

            if cursor.fetchone()[0] > 0:
                sql = (
                    f"UPDATE tblShift "
                    f"SET shift = '{job}', updating = #{updating}#, operator = '{operator}' "
                    f"WHERE uid = {uid} AND workdate = #{workdate}#"
                )
            else:
                sql = (
                    f"INSERT INTO tblShift "
                    f"(uid, workdate, shift, updating, operator) "
                    f"VALUES({uid}, #{workdate}#, '{job}', #{updating}#, '{operator}')"
                )
            cursor.execute(sql)
            conn.commit()
        cursor.close()
        print("OK")
   #dfrenzoku
    #dfskill
    #dfkinmuhyou_long
    