import datetime
from enum import Enum, auto
import locale
import logging


import pandas as pd
from decorator.convertTable import *


from util.dataReader import *

class DataName(Enum):
    kinmu = auto()
    request = auto()
    previous = auto()
    DFNrdeptcore = auto()
    RawDFNrdeptcore = auto()
    DFCore = auto()


class DataSender(DataReader):



    def __init__(self):
        super().__init__()
        self.rk = int(self.config['iota'][0])
        self.kinmu_full = None 
        

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

    def getDFstaff(self):
        uidL, staffidL, nameL = [], [], []
        for uid, person in self.members.items():
            uidL.append(uid)
            staffidL.append(person.staffid)
            nameL.append(person.name)
        unsorted = pd.DataFrame({'No':uidL, 'ID':staffidL, 'Name':nameL})
        return unsorted.sort_values(by=['No'], ascending=[True])

    def getNrdeptcore(self, dataName: DataName):
        uidL, deptL, rtL, mrL, tvL, ksL, nmL, xpL, ctL, xoL, agL, mgL, mtL=\
            [], [], [], [], [],[], [], [], [], [], [], [], [], []  


        for uid, person in self.members.items():
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

        baseDF = pd.DataFrame({'UID':uidL, 'Mo':deptL, \
            'RT':rtL, 'MR':mrL, 'TV':tvL, 'KS':ksL, 'NM':nmL ,\
            'XP':xpL, 'CT':ctL, 'XO':xoL, 'AG':agL, 'MG':mgL, 'MT':mtL})    
        
        if dataName == DataName.DFNrdeptcore:
            return baseDF['UID':'Mo']
        elif dataName == DataName.RawDFNrdeptcore:
            return baseDF
        elif dataName == DataName.DFCore:
            coreDict = {}
            coreDict['DFRTCore'] = baseDF.query('RT==6')
            coreDict['DFMRCore'] = baseDF.query('MR==6')
            coreDict['DFTVCore'] = baseDF.query('TV==6')
            coreDict['DFKSCore'] = baseDF.query('KS==6')
            coreDict['DFNMCore'] = baseDF.query('NM==6')
            coreDict['DFXPCore'] = baseDF.query('XP==6')
            coreDict['DFCTCore'] = baseDF.query('CT==6')
            coreDict['DFXOCore'] = baseDF.query('XO==6')
            coreDict['DFAGCore'] = baseDF.query('AG==6')
            coreDict['DFMGCore'] = baseDF.query('MG==6')
            coreDict['DFMTCore'] = baseDF.query('MT==6')
            return coreDict 
        else:
            pass

    @Debugger.toCSV
    def getDFSkill(self):
        uidL, agNightL, mrNightL, ctNightL, fDayL, nightL, dayL = \
            [], [], [], [], [], [], []
        for uid, person in self.members.items():
            try:
                if uid >= 900:
                    continue
                uidL.append(uid)
                agNightL.append(person.skill[0])
                mrNightL.append(person.skill[1])
                ctNightL.append(person.skill[2])
                fDayL.append(person.skill[3])
                nightL.append(person.skill[4])
                dayL.append(person.skill[5])
            except IndexError as ex :
                print(uid)
                print(person.skill)
                print(ex)
                continue
        return pd.DataFrame({'UID':uidL, 'A夜':agNightL, 'M夜':mrNightL, \
            'C夜':ctNightL, 'F':fDayL, '夜勤':nightL, '日勤':dayL})

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

    @Debugger.toCSV
    def getDFKinmuFull(self):
        previous = self.getDFPreviousOnly()
        now_next = self.getDFKinmuOnly()
        self.kinmu_full = pd.concat([previous, now_next], axis=1)
        return self.kinmu_full 
        
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
        
        df.replace(['7', '40', '41', '10', '50', '11', '60', '61', '63'], None, inplace=True)
        df.replace(['0', '1', '2', '3', '4', '5', '6', '8', '9', '62', '12'], '1', inplace=True)


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


    def getDFShift(self):
        uidL, dateL, jobL = [], [], []

        for uid, person in self.members.items():
            for day, job in person.jobPerDay.items():
                if day >= (self.date.year, self.date.month, self.date.day) and day < self.next_month[0]:
                    uidL.append(uid)
                    dateL.append(int(day[2])-1)
                    jobL.append(job)
        return pd.DataFrame({'UID': uidL, 'Date': dateL, 'Job':jobL}) 

    
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
   #dfrenzoku
    #dfskill
    #dfkinmuhyou_long