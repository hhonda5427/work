import os, sys
import datetime
import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from util.shiftController import ShiftChannel
# from integral.src.util.shiftController import ShiftChannel



class Model(QtCore.QAbstractTableModel):

    def __init__(self, shiftChannel: ShiftChannel):
        super(Model, self).__init__()
        self._dataframe = shiftChannel.shiftCtrl.getYakinForm()
        self.undoframe = self._dataframe.copy()
        self.shiftChannel = shiftChannel
        self.uidDict = {person.name : uid  for uid, person, in self.shiftChannel.shiftCtrl.members.items()}        

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
        if role == QtCore.Qt.EditRole and value in self.uidDict.keys():
            self._dataframe.iat[index.row(), index.column()] = value
            self.rewriteDatabase(index)
            self.dataChanged.emit(index, index)
            return True
      
        return False   

    def rewriteDatabase(self, index):
        # 名前からUIDを取得
        jobList = [4, 5, 6, 0, 1, 2, 3, 3]
        newuid = self.uidDict[str(self._dataframe.iat[index.row(), index.column()])]
        olduid = self.uidDict[str(self.undoframe.iat[index.row(), index.column()])]
        strdate = self.headerData(index.row(), QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)
        date = datetime.datetime.strptime(strdate, '%Y-%m-%d')
        datetuple = tuple([date.year, date.month, date.day])
        
        job = jobList[index.column()]
        oldjob = self.shiftChannel.shiftCtrl.members[newuid].jobPerDay[datetuple]
        self.shiftChannel.shiftCtrl.members[newuid].jobPerDay[datetuple] = str(job)
        self.shiftChannel.shiftCtrl.members[olduid].jobPerDay[datetuple] = oldjob

    def refreshData(self):
        print('refresh yakinhyou')
        self._dataframe = self.shiftChannel.shiftCtrl.getYakinForm()




# 夜勤表
class nightshiftDialog(QtWidgets.QDialog):
    def __init__(self, yakinModel, parent=None):
    # def __init__(self, shiftChannel, parent=None):
        super(nightshiftDialog, self).__init__(parent)

        # self._data = shiftChannel
        # self.model = Model(self._data)
        self.model = yakinModel
        self.initui()
        


    def initui(self):
        self.view = QTableView()
        self.view.setModel(self.model)
        # self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.view.doubleClicked.connect(self.dclickevent)
        layout = QVBoxLayout()
        layout.addWidget(self.view)

        self.setLayout(layout)

    def dclickevent(self, item):

        # ダブルクリックしたデータの文字が全て英字かどうか判定する　⇒　ダミーか判定する
        if item.data().isalpha() is False:
            # self.configdialog = candidate()
            # self.configdialog.show()
            # self.candidate = CandidateWidget(self._data, self.model, item)
            # self.candidate.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            # self.candidate.show()
            pass
            
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
        self.view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
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


    '''
    候補者レコード = '氏名','休日','連続勤務回数','夜勤回数','日直回数' を出力

    候補者がいなければ休日，勤務担当スタッフを全員出力？
    '''
    def createCandidate(self):
        
        # ダブルクリックしたセルから日付を取得
        targetDayS = self.targetRow - int(self.rk)
        targetDayE = targetDayS + 1
        # pprint(self.DFkinmuhyou)
        # 取得した日付で勤務表を成形
        self.DFkinmuhyou = self.DFkinmuhyou.iloc[:, [self.targetRow, self.targetRow+1]]
        # カラム[UID]を追加
        self.DFkinmuhyou['UID'] = self.DFkinmuhyou.index.values
        # pprint(self.DFkinmuhyou)
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

            for item in DFrenzoku1.columns:
                # 休日計算(振＋休)
                DFjob.at[item, '休日'] = ((self.dfshift["Job"] == 10) & (self.dfshift["UID"] == item) | (self.dfshift["Job"] == 50) & (
                            self.dfshift["UID"] == item)).sum()
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



# def main():
#     app = QtWidgets.QApplication(sys.argv)


#     window = nightshiftDialog()
#     window.show()
#     app.exec()

# if __name__ == '__main__':
#     main()
