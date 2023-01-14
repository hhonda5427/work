import os, sys
import pandas as pd
import OpenFiles as OFS
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import *
from pprint import pprint

pd.set_option('display.max_rows',200)

class DataShimizu():
    def __init__(self):
        ed, self.dfshift, self.DFyakinhyou, data_list = OFS.shift()
        sd, self.rk , self.kn = OFS.config()
        self.dfskill, dfjob1, self.DFrenzoku = OFS.Skill()
        self.DFkinmuhyou, self.DFkinmuhyou_long, longday = OFS.kinmuhyou()
        number_of_stuff, staff_list, self.dfstaff = OFS.stuff()
        self.DFNrdeptcore, self.RawDFNrdeptcore = OFS.Nrdeptcore()

        for j in range(len(self.RawDFNrdeptcore)):
            self.RawDFNrdeptcore = self.RawDFNrdeptcore.replace({'UID': {self.dfstaff.iat[j, 0]: self.dfstaff.iat[j, 2]}})
        
        self.DFCore = {
            'DFRTCore' : self.RawDFNrdeptcore.query('RT== 6 '),
            'DFMRCore' : self.RawDFNrdeptcore.query('MR== 6 '),
            'DFTVCore' : self.RawDFNrdeptcore.query('TV== 6 '),
            'DFKSCore' : self.RawDFNrdeptcore.query('KS== 6 '),
            'DFNMCore' : self.RawDFNrdeptcore.query('NM== 6 '),
            'DFXPCore' : self.RawDFNrdeptcore.query('XP== 6 '),
            'DFCTCore' : self.RawDFNrdeptcore.query('CT== 6 '),
            'DFXOCore' : self.RawDFNrdeptcore.query('XO== 6 '),
            'DFAGCore' : self.RawDFNrdeptcore.query('AG== 6 '),
            'DFMGCore' : self.RawDFNrdeptcore.query('MG== 6 '),
            'DFMTCore' : self.RawDFNrdeptcore.query('MT== 6 '),
        }


class Model(QtCore.QAbstractTableModel):
    def __init__(self, dataframe: pd.DataFrame):
        super(Model, self).__init__()
        self._dataframe = dataframe

    def index(self, row, column, parent= QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        return self.createIndex(row, column, QtCore.QModelIndex())

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        # 色付けのコード追記

    def rowCount(self, index):
        return len(self._dataframe)

    def columnCount(self, index):
        return len(self._dataframe.columns)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._dataframe.index[section])
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def setData(self, index, value, role= QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self._dataframe.iat[index.row(), index.column()] = value
            return True
        return False   

# 夜勤表
class nightshiftDialog(QtWidgets.QDialog):
    def __init__(self, data, parent=None):
        super(nightshiftDialog, self).__init__(parent)

        self._data = data
        self.model = Model(self._data.DFyakinhyou)

        self.initui()
        
        self.view.setModel(self.model)
        self.view.doubleClicked.connect(self.dclickevent)

    def initui(self):
        self.view = QTableView()

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        self.setLayout(layout)

    def dclickevent(self, item):

        # ダブルクリックしたデータの文字が全て英字かどうか判定する　⇒　ダミーか判定する
        if item.data().isalpha() is False:
            # self.configdialog = candidate()
            # self.configdialog.show()
            self.candidate = CandidateWidget(self._data, self.model, item)
            self.candidate.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.candidate.show()
            
    def fn_get_cell_Value(self, index):
        datas = index.data()

'''
src = csvファイルを読み込んで成形したデータ
nightModel = nightshiftdialogで使用しているモデル
nightIndex = nightshiftdialogで使用しているモデルのインデックス
'''
class CandidateWidget(QtWidgets.QWidget):
    def __init__(self, src, nightModel:Model, nightIndex:QtCore.QModelIndex, parent=None):
        super().__init__(parent)
        
        self.rk = src.rk
        self.dfshift = src.dfshift.copy()
        self.dfskill = src.dfskill.copy()
        self.DFrenzoku = src.DFrenzoku.copy()
        self.DFkinmuhyou = src.DFkinmuhyou.copy()
        self.DFkinmuhyou_long = src.DFkinmuhyou.copy()
        self.dfstaff = src.dfstaff.copy()
        self.DFNrdeptcore = src.DFNrdeptcore.copy()
        self.RawDFNrdeptcore = src.RawDFNrdeptcore.copy() 
        self.DFCore = src.DFCore.copy()
        self.nightshiftModel = nightModel
        self.nightshiftModelIndex = nightIndex

        self.targetRow = nightIndex.row() + int(self.rk)
        self.targetColumn = nightIndex.column()
        self.targetData = nightIndex.data()

        self.data = self.createCandidate()
        self.model =Model(self.data)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.doubleClicked.connect(self.dclickevent)

        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def dclickevent(self, index):

        row = index.row()
        
        parentRow = self.nightshiftModelIndex.row()
        parentCol = self.nightshiftModelIndex.column()

        idx = self.model.index(row, 0, QtCore.QModelIndex())
        staff = self.model.data(idx, QtCore.Qt.DisplayRole)
        job = self.nightshiftModelIndex.model().headerData(parentCol, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        date = self.nightshiftModelIndex.model().headerData(parentRow, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)
    
        self.nightshiftModel.setData(self.nightshiftModelIndex, staff, QtCore.Qt.EditRole)
        self.close()
        print(f'{staff}__{date}__{job}')



    def createCandidate(self):
        
        # ダブルクリックしたセルから日付を取得
        targetDayS = self.targetRow - int(self.rk)
        targetDayE = targetDayS + 1
        # 取得した日付で勤務表を成形
        self.DFkinmuhyou = self.DFkinmuhyou.iloc[:, [self.targetRow, self.targetRow+1]]
        # カラム[UID]を追加
        self.DFkinmuhyou['UID'] = self.DFkinmuhyou.index.values

        # DFkinmuhyou_longからダブルクリックした日の勤務を抽出
        DFkinmuhyou_longS = self.DFkinmuhyou_long.iloc[:, [self.targetRow]]
        
        # DFkinmuhyou_longからダブルクリックした日の翌日の勤務を抽出
        DFkinmuhyou_longE = self.DFkinmuhyou_long.iloc[:, [self.targetRow+1]]

        # 勤務が休の場合は消去する
        for i in reversed(range(len(DFkinmuhyou_longS))):
            if DFkinmuhyou_longS.iat[i, 0] != "休":
                DFkinmuhyou_longS.drop(DFkinmuhyou_longS.index[[i]], inplace=True)
            if DFkinmuhyou_longE.iat[i, 0] != "休":
                DFkinmuhyou_longE.drop(DFkinmuhyou_longE.index[[i]], inplace=True)

        DFkinmuhyou_longS["UID"] = DFkinmuhyou_longS.index.values
        DFkinmuhyou_longE["UID"] = DFkinmuhyou_longE.index.values

        # 各モダリティのコアメンバーにクリックした日の勤務を結合する
        # その時の各モダリティの人数を取得する(CoreRTNo)
        CoreRT=pd.merge(self.DFCore['DFRTCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreRTNo=CoreRT.shape[0]
        CoreMR=pd.merge(self.DFCore['DFMRCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreMRNo=CoreMR.shape[0]
        CoreTV=pd.merge(self.DFCore['DFTVCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreTVNo=CoreTV.shape[0]
        CoreKS=pd.merge(self.DFCore['DFKSCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreKSNo=CoreKS.shape[0]
        CoreNM=pd.merge(self.DFCore['DFNMCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreNMNo=CoreNM.shape[0]
        CoreXP=pd.merge(self.DFCore['DFXPCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreXPNo=CoreXP.shape[0]
        CoreCT=pd.merge(self.DFCore['DFCTCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreCTNo=CoreCT.shape[0]
        CoreXO=pd.merge(self.DFCore['DFXOCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreXONo=CoreXO.shape[0]
        CoreAG=pd.merge(self.DFCore['DFAGCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreAGNo=CoreAG.shape[0]
        CoreMG=pd.merge(self.DFCore['DFMGCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreMGNo=CoreMG.shape[0]
        CoreMT=pd.merge(self.DFCore['DFMTCore'], DFkinmuhyou_longS, on="UID", how='inner')
        CoreMTNo=CoreMT.shape[0]

        DFCoreNoS = pd.DataFrame({DFkinmuhyou_longS.columns[0] + " Core" :[CoreRTNo,CoreMRNo,CoreTVNo,CoreKSNo,CoreNMNo,CoreXPNo,CoreCTNo,CoreXONo,CoreAGNo,CoreMGNo,CoreMTNo]},
                                index=['RT','MR','TV','KS','NM','XP','CT','XO','AG','MG','MT'])
        DFCoreNoS["Mo"] = DFCoreNoS.index.values

        CoreRT=pd.merge(self.DFCore['DFRTCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreRTNo=CoreRT.shape[0]
        CoreMR=pd.merge(self.DFCore['DFMRCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreMRNo=CoreMR.shape[0]
        CoreTV=pd.merge(self.DFCore['DFTVCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreTVNo=CoreTV.shape[0]
        CoreKS=pd.merge(self.DFCore['DFKSCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreKSNo=CoreKS.shape[0]
        CoreNM=pd.merge(self.DFCore['DFNMCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreNMNo=CoreNM.shape[0]
        CoreXP=pd.merge(self.DFCore['DFXPCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreXPNo=CoreXP.shape[0]
        CoreCT=pd.merge(self.DFCore['DFCTCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreCTNo=CoreCT.shape[0]
        CoreXO=pd.merge(self.DFCore['DFXOCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreXONo=CoreXO.shape[0]
        CoreAG=pd.merge(self.DFCore['DFAGCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreAGNo=CoreAG.shape[0]
        CoreMG=pd.merge(self.DFCore['DFMGCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreMGNo=CoreMG.shape[0]
        CoreMT=pd.merge(self.DFCore['DFMTCore'], DFkinmuhyou_longE, on="UID", how='inner')
        CoreMTNo=CoreMT.shape[0]

        DFCoreNoE = pd.DataFrame({DFkinmuhyou_longE.columns[0] + " Core" :[CoreRTNo,CoreMRNo,CoreTVNo,CoreKSNo,CoreNMNo,CoreXPNo,CoreCTNo,CoreXONo,CoreAGNo,CoreMGNo,CoreMTNo]},
                                index=['RT','MR','TV','KS','NM','XP','CT','XO','AG','MG','MT'])
        DFCoreNoE["Mo"] = DFCoreNoE.index.values

        '''
        TargetColumn==0, 1, 2 夜勤の場合
            DFkinmuhyouで勤務がNoneで無ければ削除　ここでのDFkimuhyouはターゲット日とその翌日のみ切り出したもの
        TagetColumn!=0, 1, 2 日勤の場合
            DFkinmuhyouで当日の勤務がNoneで無ければ削除

        DFkinmuhyouには勤務対象者のみが残る
        '''
        if self.targetColumn == 0 or 1 or 2 :
            for i in reversed(range(len(self.DFkinmuhyou))):
                if self.DFkinmuhyou.iat[i, 0] != "" or self.DFkinmuhyou.iat[i, 1] != "":
                    self.DFkinmuhyou.drop(self.DFkinmuhyou.index[[i]], inplace=True)
            # print(dfskill)
        else:
            for i in reversed(range(len(self.DFkinmuhyou))):
                if self.DFkinmuhyou.iat[i, 0] != "":
                    self.DFkinmuhyou.drop(self.DFkinmuhyou.index[[i]], inplace=True)

        '''
        dfskill = ["UID", "A夜", "M夜", "C夜", "F日", "夜勤", "日直"]レコードのUIDを名前に変更
        DFkakunin = dfskillにターゲット日の勤務を結合
        TargetColumnに応じてDFkakuninの勤務で切り出す
        DFkakuninUID = DFkakuninをUID（氏名）だけにした配列
        '''
        for j in range(len(self.dfskill)):
            self.dfskill = self.dfskill.replace({'UID': {self.dfstaff.iat[j, 0]: self.dfstaff.iat[j, 2]}})
        # pprint(dfskill)
        # print(DFkinmuhyou)

        DFkakunin = pd.merge(self.dfskill, self.DFkinmuhyou, on="UID", how='inner')
        # pprint(DFkakunin)
        if self.targetColumn == 0:
            DFkakunin = DFkakunin[(DFkakunin["A夜"] > 0) & (DFkakunin["夜勤"] > 0)]
        elif self.targetColumn == 1:
            DFkakunin = DFkakunin[(DFkakunin["M夜"] > 0) & (DFkakunin["夜勤"] > 0)]
        elif self.targetColumn == 2:
            DFkakunin = DFkakunin[(DFkakunin["C夜"] > 0) & (DFkakunin["夜勤"] > 0)]
        elif self.targetColumn == 3:
            DFkakunin = DFkakunin[(DFkakunin["A夜"] > 0) & (DFkakunin["日直"] > 0)]
        elif self.targetColumn == 4:
            DFkakunin = DFkakunin[(DFkakunin["M夜"] > 0) & (DFkakunin["日直"] > 0)]
        elif self.targetColumn == 5:
            DFkakunin = DFkakunin[(DFkakunin["C夜"] > 0) & (DFkakunin["日直"] > 0)]
        elif self.targetColumn == 6:
            DFkakunin = DFkakunin[(DFkakunin["日直"] > 0)]

        DFkakuninUID = DFkakunin["UID"]

        # if len(DFkakuninUID.index) >> 0:
        if len(DFkakuninUID.index) > 0:
            for i in range(len(self.dfstaff)):
                # UID(名前）をUIDに変更
                DFkakuninUID = DFkakuninUID.replace(self.dfstaff.iat[i, 2], self.dfstaff.iat[i, 0])
            # pprint(DFkakuninUID)
            DFkakuninUID.index = DFkakuninUID

            DFr = pd.merge(self.DFrenzoku, DFkakuninUID, how='inner', left_index=True, right_index=True)
            # pprint(DFr)
            DFrenzokuRAW = DFr.drop('UID', axis=1)
            # pprint(DFrenzokuRAW)

            '''
            DFrenzoku = 勤務交代可能なスタッフのみを抽出し,各日付で勤務が可能な日に1を割り当てた勤務表
            ダブルクリックした対象日と翌日を勤務にした場合のDFrenzokuを作成
            DFrenzoku1 = 勤務の累積和を求めて最も大きい連続勤務数を取得する
            DF = 対象スタッフに対して勤務を割り当てた場合の連続勤務数の配列
            '''
            self.DFrenzoku = DFrenzokuRAW

            # TargetColumnに勤務入力

            # print(f'{TargetDayS}___{TargetDayE}')
            # pprint(DFrenzoku)
            self.DFrenzoku[targetDayS] = 1
            self.DFrenzoku[targetDayE] = 1
            # pprint(DFrenzoku)
            
            # DFrenzoku.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFrenzoku1.csv", encoding='Shift_JIS')
            # 連続勤務
            # print('start')
            DFrenzoku1 = self.DFrenzoku.T  # 転置
            # pprint(DFrenzoku1)
            DF = pd.DataFrame(index=DFkakuninUID.to_list(), columns=['連続勤務日'])
            # pprint(DF)
            for item in DFrenzoku1.columns:  # 遅い
                y = DFrenzoku1.loc[:, item]
                # 対象列の連続する値を累積和を求める
                DFrenzoku1['new'] = y.groupby((y != y.shift()).cumsum()).cumcount() + 1
                DF.loc[item, ['連続勤務日']] = DFrenzoku1['new'].max()
            # print('end')


            '''
            DFjob = 勤務交代対象スタッフの休日数,連続勤務回数,夜勤回数,日直回数,UIDの配列

            
            '''
            DFjob = pd.DataFrame(index=DFkakuninUID.to_list(), columns=['休日', '連続勤務回数', '夜勤回数', "日直回数"])
            DFjob["UID"] = DFkakuninUID.to_list()
            DFrenzoku1 = DFrenzoku1.drop('new', axis=1)
            # dfshiftRAW = self.dfshift
            # pprint(DFjob)
            # pprint(DFrenzoku1)
            # 0勤務7明
            # for item in DFrenzoku1.columns:
            #     # dfshift=[UID, Date, Job]のレコードセットからUIDとDateを指定してレコードのindexの値を取得する
            #     IV = dfshift[(dfshift['UID'] == item) & (dfshift['Date'] == TargetDayS)]['UID'].index.values
            #     print(IV)
            #     # クリックした列がアンギオ夜勤であれば
            #     if TargetColumn == 0:
            #         dfshift.at[IV[0], 'Job'] = 4
            #     IV = dfshift[(dfshift['UID'] == item) & (dfshift['Date'] == TargetDayE)]['UID'].index.values
            #     dfshift.at[IV[0], 'Job'] = 7

            for item in DFrenzoku1.columns:
                # 休日計算(振＋休)
                DFjob.at[item, '休日'] = ((self.dfshift["Job"] == 10) & (self.dfshift["UID"] == item) | (self.dfshift["Job"] == 50) & (
                            self.dfshift["UID"] == item)).sum()
                # print('sum_sum')
                # print(((dfshift["Job"] == 10) & (dfshift["UID"] == item) | (dfshift["Job"] == 50) & (
                #             dfshift["UID"] == item)).sum().sum())
                # print('__________sum__________')
                # print(((dfshift["Job"] == 10) & (dfshift["UID"] == item) | (dfshift["Job"] == 50) & (
                #             dfshift["UID"] == item)).sum())
                # 連続回数
                DFjob.at[item, '連続勤務回数'] = DF.at[item, '連続勤務日']
                # 夜勤回数(明で計算)
                DFjob.at[item, '夜勤回数'] = ((self.dfshift["Job"] == 4) & (self.dfshift["UID"] == item) | (self.dfshift["Job"] == 5) & (self.dfshift["UID"] == item) | (self.dfshift["Job"] == 6) & (self.dfshift["UID"] == item)).sum()
                # 日直回数
                DFjob.at[item, '日直回数'] = ((self.dfshift["Job"] == 0) & (self.dfshift["UID"] == item) | (self.dfshift["Job"] == 1) & (
                            self.dfshift["UID"] == item) | (self.dfshift["Job"] == 2) & (self.dfshift["UID"] == item) | (
                                                      self.dfshift["Job"] == 3) & (self.dfshift["UID"] == item)).sum()
            DFjob = DFjob.reindex(columns=['UID','休日','連続勤務回数','夜勤回数','日直回数'])
            DFjob=pd.merge(DFjob, self.DFNrdeptcore, on="UID", how='inner')
            for j in range(len(self.dfskill)):
                DFjob = DFjob.replace({'UID': {self.dfstaff.iat[j, 0]: self.dfstaff.iat[j, 2]}})

            DFjob= pd.merge(DFjob, DFCoreNoS,on="Mo", how='inner')
            DFjob= pd.merge(DFjob, DFCoreNoE,on="Mo", how='inner')
            DFjob = DFjob.reindex(columns=['UID','Mo', DFkinmuhyou_longS.columns[0] + " Core",DFkinmuhyou_longE.columns[0] + " Core",'休日','連続勤務回数','夜勤回数','日直回数'])
            
            return DFjob



# # ダブルクリックイベント-編集用
# class candidate(QtWidgets.QDialog):
#     def __init__(self, parent=None):
#         super(candidate, self).__init__(parent)
#         self.initui()

#     def initui(self):
#         ui_path = "ui_files"
#         self.ui = uic.loadUi(f"{ui_path}/dialog.ui", baseinstance=self)
#         #必要データ読み込み

#         '''
#         sd = 基準日(yyyy/mm/dd),
#         rk = 連続勤務，
#         kn = 休日数
#         '''
#         sd, rk , kn = OFS.config()
#         '''
#         dfskill = ["UID", "A夜", "M夜", "C夜", "F日", "夜勤", "日直"]のレコード
#         dfjob1 = [UID, Date, Job] 勤務が1, それ以外はNoneとなっている
#         DFrenzoku =  dfjob1を勤務表形式に変化したtable
#         '''
#         dfskill, dfjob1, DFrenzoku = OFS.Skill()
#         '''
#         DFkinmuhyou = 今月のリクエスト＋夜勤のみの勤務表
#         DFkinmuhyou_long = previous + shiftの勤務表
#         longday = DFkinmuhyouのカラムヘッダー（基準日を０とした日付）
#         '''
#         DFkinmuhyou, DFkinmuhyou_long, longday = OFS.kinmuhyou()
#         '''
#         ed = 月末
#         dfshift = [UID, date, shift] , 
#         DFyakinhyou = 夜勤表 , 
#         data_list = 基準日を0とした日付のリスト
#         '''
#         ed, dfshift, DFyakinhyou, data_list = OFS.shift()
#         '''
#         number_of_stuff = スタッフ数
#         staff_list = UIDリスト
#         dfstaff = [UID, ID, Name]のリスト
#         '''
#         number_of_stuff, staff_list, dfstaff = OFS.stuff()
#         '''
#         DFNrdeptcore = [UID, Modality]のレコード
#         RawDFNrdeptcore = ["UID", "Mo", "RT", "MR", "TV", "KS", "NM", "XP", "CT", "XO", "AG", "MG", "MT"]
#         '''
#         DFNrdeptcore,RawDFNrdeptcore = OFS.Nrdeptcore()
#         #ダブルクリックしたセルからターゲットの日付(0-30)
#         TargetDayS = TargetRow - int(rk)
#         # print(TargetDayS)
#         TargetDayE = TargetDayS + 1
#         # ダブルクリックした日とその翌日の勤務を抽出する
#         DFkinmuhyou = DFkinmuhyou.iloc[:, [TargetRow, TargetRow+1]]

#         # カラム[UID]を追加
#         DFkinmuhyou["UID"] = DFkinmuhyou.index.values

#         # DFkinmuhyou.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFrenzoku21.csv", encoding='Shift_JIS')

#         #Coreメンバーの数計算
#         # UIDから名前へ変換
#         for j in range(len(RawDFNrdeptcore)):
#             RawDFNrdeptcore = RawDFNrdeptcore.replace({'UID': {dfstaff.iat[j, 0]: dfstaff.iat[j, 2]}})
        
#         # 各モダリティのコアメンバー抽出
#         DFRTCore = RawDFNrdeptcore.query('RT== 6 ')
#         DFMRCore = RawDFNrdeptcore.query('MR== 6 ')
#         DFTVCore = RawDFNrdeptcore.query('TV== 6 ')
#         DFKSCore = RawDFNrdeptcore.query('KS== 6 ')
#         DFNMCore = RawDFNrdeptcore.query('NM== 6 ')
#         DFXPCore = RawDFNrdeptcore.query('XP== 6 ')
#         DFCTCore = RawDFNrdeptcore.query('CT== 6 ')
#         DFXOCore = RawDFNrdeptcore.query('XO== 6 ')
#         DFAGCore = RawDFNrdeptcore.query('AG== 6 ')
#         DFMGCore = RawDFNrdeptcore.query('MG== 6 ')
#         DFMTCore = RawDFNrdeptcore.query('MT== 6 ')
        
#         # DFkinmuhyou_longからダブルクリックした日の勤務を抽出
#         DFkinmuhyou_longS = DFkinmuhyou_long.iloc[:, [TargetRow]]
#         print('_____________*************____________')
#         print(DFkinmuhyou_longS)
#         print('_____________*************____________')
#         # DFkinmuhyou_longからダブルクリックした日の翌日の勤務を抽出
#         DFkinmuhyou_longE = DFkinmuhyou_long.iloc[:, [TargetRow+1]]
#         print(DFkinmuhyou_longE)
#         print('_____________*************____________')
#         #本当は勤務

#         # 勤務が休の場合は消去する
#         for i in reversed(range(len(DFkinmuhyou_longS))):
#             if DFkinmuhyou_longS.iat[i, 0] != "休":
#                 DFkinmuhyou_longS.drop(DFkinmuhyou_longS.index[[i]], inplace=True)

#         for i in reversed(range(len(DFkinmuhyou_longE))):
#             if DFkinmuhyou_longE.iat[i, 0] != "休":
#                 DFkinmuhyou_longE.drop(DFkinmuhyou_longE.index[[i]], inplace=True)

#         DFkinmuhyou_longS["UID"] = DFkinmuhyou_longS.index.values
#         DFkinmuhyou_longE["UID"] = DFkinmuhyou_longE.index.values
#         # 各モダリティのコアメンバーにクリックした日の勤務を結合する
#         # その時の各モダリティの人数を取得する(CoreRTNo)
#         CoreRT=pd.merge(DFRTCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreRTNo=CoreRT.shape[0]
#         CoreMR=pd.merge(DFMRCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreMRNo=CoreMR.shape[0]
#         CoreTV=pd.merge(DFTVCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreTVNo=CoreTV.shape[0]
#         CoreKS=pd.merge(DFKSCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreKSNo=CoreKS.shape[0]
#         CoreNM=pd.merge(DFNMCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreNMNo=CoreNM.shape[0]
#         CoreXP=pd.merge(DFXPCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreXPNo=CoreXP.shape[0]
#         CoreCT=pd.merge(DFCTCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreCTNo=CoreCT.shape[0]
#         CoreXO=pd.merge(DFXOCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreXONo=CoreXO.shape[0]
#         CoreAG=pd.merge(DFAGCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreAGNo=CoreAG.shape[0]
#         CoreMG=pd.merge(DFMGCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreMGNo=CoreMG.shape[0]
#         CoreMT=pd.merge(DFMTCore, DFkinmuhyou_longS, on="UID", how='inner')
#         CoreMTNo=CoreMT.shape[0]

#         # 

#         '''
#         DFCoreNoS = ターゲット日の各モダリティのコアメンバーの人数
#         DFCoreNoE = ターゲット翌日の各モダリティのコアメンバーの人数
#             04/09 Core  Mo
#         RT           6  RT
#         MR           4  MR
#         TV           7  TV
#         KS           4  KS
#         NM           3  NM
#         XP           8  XP
#         CT           8  CT
#         XO           9  XO
#         AG           5  AG
#         MG           0  MG
#         MT           0  MT
#         '''
#         DFCoreNoS = pd.DataFrame({DFkinmuhyou_longS.columns[0] + " Core" :[CoreRTNo,CoreMRNo,CoreTVNo,CoreKSNo,CoreNMNo,CoreXPNo,CoreCTNo,CoreXONo,CoreAGNo,CoreMGNo,CoreMTNo]},
#                                 index=['RT','MR','TV','KS','NM','XP','CT','XO','AG','MG','MT'])
#         DFCoreNoS["Mo"] = DFCoreNoS.index.values

#         CoreRT=pd.merge(DFRTCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreRTNo=CoreRT.shape[0]
#         CoreMR=pd.merge(DFMRCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreMRNo=CoreMR.shape[0]
#         CoreTV=pd.merge(DFTVCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreTVNo=CoreTV.shape[0]
#         CoreKS=pd.merge(DFKSCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreKSNo=CoreKS.shape[0]
#         CoreNM=pd.merge(DFNMCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreNMNo=CoreNM.shape[0]
#         CoreXP=pd.merge(DFXPCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreXPNo=CoreXP.shape[0]
#         CoreCT=pd.merge(DFCTCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreCTNo=CoreCT.shape[0]
#         CoreXO=pd.merge(DFXOCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreXONo=CoreXO.shape[0]
#         CoreAG=pd.merge(DFAGCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreAGNo=CoreAG.shape[0]
#         CoreMG=pd.merge(DFMGCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreMGNo=CoreMG.shape[0]
#         CoreMT=pd.merge(DFMTCore, DFkinmuhyou_longE, on="UID", how='inner')
#         CoreMTNo=CoreMT.shape[0]

#         DFCoreNoE = pd.DataFrame({DFkinmuhyou_longE.columns[0] + " Core" :[CoreRTNo,CoreMRNo,CoreTVNo,CoreKSNo,CoreNMNo,CoreXPNo,CoreCTNo,CoreXONo,CoreAGNo,CoreMGNo,CoreMTNo]},
#                                 index=['RT','MR','TV','KS','NM','XP','CT','XO','AG','MG','MT'])
#         DFCoreNoE["Mo"] = DFCoreNoE.index.values
#         # print(DFCoreNoE)

#         # 日当直に入れるかの予定確認(UID出力)
#         # print(TargetColumn)
#         # TargetColumn = nightshiftDialog->dclickevetでglobal変数として設定

#         '''
#         TargetColumn==0, 1, 2 夜勤の場合
#             DFkinmuhyouで勤務がNoneで無ければ削除　ここでのDFkimuhyouはターゲット日とその翌日のみ切り出したもの
#         TagetColumn!=0, 1, 2 日勤の場合
#             DFkinmuhyouで当日の勤務がNoneで無ければ削除

#         DFkinmuhyouには勤務対象者のみが残る
#         '''
#         if TargetColumn == 0 or 1 or 2 :
#             for i in reversed(range(len(DFkinmuhyou))):
#                 if DFkinmuhyou.iat[i, 0] != "" or DFkinmuhyou.iat[i, 1] != "":
#                     DFkinmuhyou.drop(DFkinmuhyou.index[[i]], inplace=True)
#             # print(dfskill)
#         else:
#             for i in reversed(range(len(DFkinmuhyou))):
#                 if DFkinmuhyou.iat[i, 0] != "":
#                     DFkinmuhyou.drop(DFkinmuhyou.index[[i]], inplace=True)

#         '''
#         dfskill = ["UID", "A夜", "M夜", "C夜", "F日", "夜勤", "日直"]レコードのUIDを名前に変更
#         DFkakunin = dfskillにターゲット日の勤務を結合
#         TargetColumnに応じてDFkakuninの勤務で切り出す
#         DFkakuninUID = DFkakuninをUID（氏名）だけにした配列
#         '''
#         for j in range(len(dfskill)):
#             dfskill = dfskill.replace({'UID': {dfstaff.iat[j, 0]: dfstaff.iat[j, 2]}})
#         # pprint(dfskill)
#         # print(DFkinmuhyou)

#         DFkakunin = pd.merge(dfskill, DFkinmuhyou, on="UID", how='inner')
#         pprint(DFkakunin)
#         if TargetColumn == 0:
#             DFkakunin = DFkakunin[(DFkakunin["A夜"] > 0) & (DFkakunin["夜勤"] > 0)]
#         elif TargetColumn == 1:
#             DFkakunin = DFkakunin[(DFkakunin["M夜"] > 0) & (DFkakunin["夜勤"] > 0)]
#         elif TargetColumn == 2:
#             DFkakunin = DFkakunin[(DFkakunin["C夜"] > 0) & (DFkakunin["夜勤"] > 0)]
#         elif TargetColumn == 3:
#             DFkakunin = DFkakunin[(DFkakunin["A夜"] > 0) & (DFkakunin["日直"] > 0)]
#         elif TargetColumn == 4:
#             DFkakunin = DFkakunin[(DFkakunin["M夜"] > 0) & (DFkakunin["日直"] > 0)]
#         elif TargetColumn == 5:
#             DFkakunin = DFkakunin[(DFkakunin["C夜"] > 0) & (DFkakunin["日直"] > 0)]
#         elif TargetColumn == 6:
#             DFkakunin = DFkakunin[(DFkakunin["日直"] > 0)]

#         DFkakuninUID = DFkakunin["UID"]

#         # if len(DFkakuninUID.index) >> 0:
#         if len(DFkakuninUID.index) > 0:
#             for i in range(len(dfstaff)):
#                 # UID(名前）をUIDに変更
#                 DFkakuninUID = DFkakuninUID.replace(dfstaff.iat[i, 2], dfstaff.iat[i, 0])
#             pprint(DFkakuninUID)
#             DFkakuninUID.index = DFkakuninUID

#             DFr = pd.merge(DFrenzoku, DFkakuninUID, how='inner', left_index=True, right_index=True)
#             pprint(DFr)
#             DFrenzokuRAW = DFr.drop('UID', axis=1)
#             pprint(DFrenzokuRAW)

#             '''
#             DFrenzoku = 勤務交代可能なスタッフのみを抽出し，各日付で勤務が可能な日に1を割り当てた勤務表
#             ダブルクリックした対象日と翌日を勤務にした場合のDFrenzokuを作成
#             DFrenzoku1 = 勤務の累積和を求めて最も大きい連続勤務数を取得する
#             DF = 対象スタッフに対して勤務を割り当てた場合の連続勤務数の配列
#             '''
#             DFrenzoku = DFrenzokuRAW

#             # DFrenzoku.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFrenzoku2.csv", encoding='Shift_JIS')
#             # TargetColumnに勤務入力

#             # print(f'{TargetDayS}___{TargetDayE}')
#             # pprint(DFrenzoku)
#             DFrenzoku[TargetDayS] = 1
#             DFrenzoku[TargetDayE] = 1
#             # pprint(DFrenzoku)
            
#             # DFrenzoku.to_csv("C:/Users/pelu0/Desktop/20221220/sample1/DFrenzoku1.csv", encoding='Shift_JIS')
#             # 連続勤務
#             # print('start')
#             DFrenzoku1 = DFrenzoku.T  # 転置
#             # pprint(DFrenzoku1)
#             DF = pd.DataFrame(index=DFkakuninUID.to_list(), columns=['連続勤務日'])
#             # pprint(DF)
#             for item in DFrenzoku1.columns:  # 遅い
#                 y = DFrenzoku1.loc[:, item]
#                 # 対象列の連続する値を累積和を求める
#                 DFrenzoku1['new'] = y.groupby((y != y.shift()).cumsum()).cumcount() + 1
#                 DF.loc[item, ['連続勤務日']] = DFrenzoku1['new'].max()
#             # print('end')


#             '''
#             DFjob = 勤務交代対象スタッフの休日数，連続勤務回数，夜勤回数，日直回数，UIDの配列

            
#             '''
#             # 現状確認
#             DFjob = pd.DataFrame(index=DFkakuninUID.to_list(), columns=['休日', '連続勤務回数', '夜勤回数', "日直回数"])
#             DFjob["UID"] = DFkakuninUID.to_list()
#             DFrenzoku1 = DFrenzoku1.drop('new', axis=1)
#             dfshiftRAW = dfshift
#             pprint(DFjob)
#             pprint(DFrenzoku1)
#             # 0勤務7明
#             for item in DFrenzoku1.columns:
#                 # dfshift=[UID, Date, Job]のレコードセットからUIDとDateを指定してレコードのindexの値を取得する
#                 IV = dfshift[(dfshift['UID'] == item) & (dfshift['Date'] == TargetDayS)]['UID'].index.values
#                 print(IV)
#                 # クリックした列がアンギオ夜勤であれば
#                 if TargetColumn == 0:
#                     dfshift.at[IV[0], 'Job'] = 4
#                 IV = dfshift[(dfshift['UID'] == item) & (dfshift['Date'] == TargetDayE)]['UID'].index.values
#                 dfshift.at[IV[0], 'Job'] = 7

#             # print(dfshift)

#             for item in DFrenzoku1.columns:
#                 # 休日計算(振＋休)
#                 DFjob.at[item, '休日'] = ((dfshift["Job"] == 10) & (dfshift["UID"] == item) | (dfshift["Job"] == 50) & (
#                             dfshift["UID"] == item)).sum().sum()
#                 # print('sum_sum')
#                 # print(((dfshift["Job"] == 10) & (dfshift["UID"] == item) | (dfshift["Job"] == 50) & (
#                 #             dfshift["UID"] == item)).sum().sum())
#                 # print('__________sum__________')
#                 # print(((dfshift["Job"] == 10) & (dfshift["UID"] == item) | (dfshift["Job"] == 50) & (
#                 #             dfshift["UID"] == item)).sum())
#                 # 連続回数
#                 DFjob.at[item, '連続勤務回数'] = DF.at[item, '連続勤務日']
#                 # 夜勤回数(明で計算)
#                 DFjob.at[item, '夜勤回数'] = ((dfshift["Job"] == 4) & (dfshift["UID"] == item) | (dfshift["Job"] == 5) & (dfshift["UID"] == item) | (dfshift["Job"] == 6) & (dfshift["UID"] == item)).sum().sum()
#                 # 日直回数
#                 DFjob.at[item, '日直回数'] = ((dfshift["Job"] == 0) & (dfshift["UID"] == item) | (dfshift["Job"] == 1) & (
#                             dfshift["UID"] == item) | (dfshift["Job"] == 2) & (dfshift["UID"] == item) | (
#                                                       dfshift["Job"] == 3) & (dfshift["UID"] == item)).sum().sum()
#             DFjob = DFjob.reindex(columns=['UID','休日','連続勤務回数','夜勤回数','日直回数'])
#             DFjob=pd.merge(DFjob, DFNrdeptcore, on="UID", how='inner')
#             for j in range(len(dfskill)):
#                 DFjob = DFjob.replace({'UID': {dfstaff.iat[j, 0]: dfstaff.iat[j, 2]}})

#             DFjob= pd.merge(DFjob, DFCoreNoS,on="Mo", how='inner')
#             DFjob= pd.merge(DFjob, DFCoreNoE,on="Mo", how='inner')
#             DFjob = DFjob.reindex(columns=['UID','Mo', DFkinmuhyou_longS.columns[0] + " Core",DFkinmuhyou_longE.columns[0] + " Core",'休日','連続勤務回数','夜勤回数','日直回数'])
#             data = DFjob
#             # DFjob.to_csv("C:/Users/pelu0/Desktop/20221220/sample1DFjob.csv", encoding='Shift_JIS')

#             self.model = Model(data)
#             self.ui.tableView.setModel(self.model)
#             self.ui.tableView.doubleClicked.connect(self.clickevent)

#         else:
#             messagebox.showinfo('注意!!!','候補者がいません.')





#     def clickevent(self, item):
#         ed, dfshift, DFyakinhyou, data_list = OFS.shift()
#         number_of_stuff, staff_list, dfstaff = OFS.stuff()
#         sd, rk, kn = OFS.config()
#         DFjob = pd.read_csv("C:/Users/pelu0/Desktop/20221220/sample1DFjob.csv", encoding='Shift_JIS')

#         messagebox.showwarning(title="Warning", message="一度変更すると戻せません.")
#         TargetR = item.row()
#         TargetC = item.column()
#         TargetD = item.data()

#         b=DFjob.iloc[TargetR, 2]
#         #名前変換(名前→ID)
#         DFTargetDID = dfstaff[dfstaff['Name'] == TargetD]
#         TargetDID = DFTargetDID.iloc[0,0]
#         TargetDayS = TargetRow - int(rk)
#         TargetDayE = TargetDayS + 1

#         if TargetColumn == 0:
#             # dfshift.to_csv("C:/Users/pelu0/Desktop/20221220/sample1Predfshift.csv", encoding='Shift_JIS')
#             ret = messagebox.askokcancel('最終確認!!!',TargetD + 'さんのA夜勤を'+'入れますか？')
#             if ret == True:
#                 IV = dfshift[(dfshift['UID'] == TargetDID) & (dfshift['Date'] == TargetDayS)]['UID'].index.values
#                 dfshift.at[IV[0], 'Job'] = 4
#                 IV = dfshift[(dfshift['UID'] == TargetDID) & (dfshift['Date'] == TargetDayE)]['UID'].index.values
#                 dfshift.at[IV[0], 'Job'] = 7
#                 c=int(kn)
#                 b=int(b)
#                 a = c - b
#                 a = str(a)
#                 messagebox.showinfo('決定', TargetD +'さんの振替休日'+ a +'日を設定してください.')


def main():
    app = QtWidgets.QApplication(sys.argv)

    data = DataShimizu()
    window = nightshiftDialog(data)
    window.show()
    app.exec()

if __name__ == '__main__':
    main()