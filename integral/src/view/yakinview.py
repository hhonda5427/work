import datetime

import numpy as np
import pandas
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from util.shiftController import ShiftChannel
from util.dataSender import DataName
from .view import TableModel


# from integral.src.util.shiftController import ShiftChannel

class CandidateModel(TableModel):
    def __init__(self, df, parent=None, *args):
        super().__init__(self, parent, *args)
        self._data = df


class Model(QtCore.QAbstractTableModel):
    def __init__(self, shiftChannel: ShiftChannel):
        super(Model, self).__init__()
        self.shiftChannel = shiftChannel
        # self._uidframe = shiftChannel.shiftCtrl.getYakinForm_uid()
        # print(self._uidframe)
        self._dataframe = shiftChannel.shiftCtrl.getYakinForm()
        self.undoframe = self._dataframe.copy()
        self.uidDict = {person.name: uid for uid, person, in self.shiftChannel.shiftCtrl.members.items()}
        self.rows,self.cols = self._dataframe.shape
        self._colorPlace = {col: {row: QColor('#00000000') for row in range(self.rows)} for col in range(self.cols)}
        #初期状態の文字色は黒
        # self._wordColor =  {col: {row: QColor('#000000') for row in range(self.rows)} for col in range(self.cols)}
        # self._wordColorのshapeを確認
        # self.matching_cells = []
        self._textColor = pd.DataFrame(data=[[QColor('#000000') for j in range(len(self._dataframe.columns))] for i in range(len(self._dataframe))])
        self._font = pd.DataFrame(data=[[False for j in range(len(self._dataframe.columns))] for i in range(len(self._dataframe))])
        # self.shiftChanel.shiftCtrl.membersのすべてのkeyに対して、wordColorGenを実行し、辞書を生成
        # self.wordColorDict = {uid: self.wordColorGen(uid) for uid in self.shiftChannel.shiftCtrl.members.keys()}

        # Dummyの場所（編集できる場所）
        self.DummyPlace = []
        for i in range(self.rows):
            for j in range(self.cols):
                if 'dummy' in self._dataframe.iloc[i, j]:
                    dummy_place = (i, j)
                    self.DummyPlace.append(dummy_place)
                    self._colorPlace[j][i] = QColor('#EBFF00')

    def textColorGen(self, idx):

        name = self._dataframe.iat[idx.row(), idx.column()]
        if name is None:
            return None

        template = []

        idx_row, idx_col = np.where(self._dataframe.values == name)
  
        if len(idx_row) > 0:
            for i in range(len(idx_row)):
                template.append((idx_row[i], idx_col[i]))

            return template

        else:
            return None
        
    # def wordColorGen(self, uid):

    #     #self._wordColorと同じshapeの空の辞書を作成
    #     template =  {col: {row: QColor('#000000') for row in range(self.rows)} for col in range(self.cols)}

    #     # 引数のuidと一致する要素のインデックスをすべて取得
    #     idx = np.where(self._uidframe.values == uid)

    #     if len(idx[0]) > 0:
    #         # idxにあるインデックスすべてに対して、templateの要素を変更
    #         for i in range(len(idx[0])):
    #             # templateの変更には、オレンジ色を設定
    #             template[idx[1][i]][idx[0][i]] = QColor('#FFA500')
    #         return template
            
    #     else:
    #         return None
        

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        return self.createIndex(row, column, QtCore.QModelIndex())

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        # 色付けのコード追記
        if role == QtCore.Qt.ItemDataRole.BackgroundColorRole:
            return self._colorPlace[index.column()][index.row()]
        if role == QtCore.Qt.ItemDataRole.ForegroundRole:
            # indexにあるQColorのhex色を確認
            return self._textColor[index.column()][index.row()]
        
        elif role == QtCore.Qt.FontRole:            
            font = QtGui.QFont()   
            flg = self._font.iat[index.row(), index.column()]
            font.setBold(flg)
            font.setItalic(flg)
            return QtCore.QVariant(font)

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

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        # もしroleがEditRoleで、valueが現在保持されているUNIQUE IDに含まれていたら実行
        if role == QtCore.Qt.EditRole and value in self.uidDict.keys():
            # データフレームの値を変更する
            self._dataframe.iat[index.row(), index.column()] = value
            # データベースの情報を更新する
            self.rewriteDatabase(index)
            # dataChangedシグナルを発生させて表示の更新を要求する
            self.dataChanged.emit(index, index)
            return True
        elif role == QtCore.Qt.ForegroundRole:

            self._textColor.iat[index.row(), index.column()] = value
            return True
        elif role == QtCore.Qt.FontRole:
        
            self._font.iat[index.row(), index.column()] = value
            return True
        # 上記条件以外ならFalseを返す
        return False
    
    def rewriteDatabase(self, index):
        # 名前からUIDを取得
        # 'A夜勤', 5: 'M夜勤', 6: 'C夜勤', 0: 'A日勤', 1: 'M日勤', 2: 'C日勤', 3: 'F日勤', -3: 'F日勤'
        jobList = ['4', '5', '6', '0', '1', '2', '3', '3']
        newuid = self.uidDict[str(self._dataframe.iat[index.row(), index.column()])]
        olduid = self.uidDict[str(self.undoframe.iat[index.row(), index.column()])]
        strdate = self.headerData(index.row(), QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)
        date = datetime.datetime.strptime(strdate, '%Y-%m-%d')
        datetuple = tuple([date.year, date.month, date.day])
        job = jobList[index.column()]
        oldjob = self.shiftChannel.shiftCtrl.members[newuid].jobPerDay[datetuple]
        self.shiftChannel.shiftCtrl.members[newuid].jobPerDay[datetuple] = job
        self.shiftChannel.shiftCtrl.members[olduid].jobPerDay[datetuple] = oldjob

        # 夜勤の場合
        if jobList[index.column()] == '4' or jobList[index.column()] == '5' or jobList[index.column()] == '6':
            datetuple1 = tuple([date.year, date.month, date.day + 1])
            job1 = '7'
            oldjob1 = self.shiftChannel.shiftCtrl.members[newuid].jobPerDay[datetuple1]
            self.shiftChannel.shiftCtrl.members[newuid].jobPerDay[datetuple1] = job1
            self.shiftChannel.shiftCtrl.members[olduid].jobPerDay[datetuple1] = oldjob1
        self.undoframe = self._dataframe.copy()

    def refreshData(self):
        self._dataframe = self.shiftChannel.shiftCtrl.getYakinForm()
        

    # def update_cell_color(self, selected, deselected):
    #     # 選択が外れたとき -> 何もしなくていい
    #     # for _index in deselected.indexes():

    #     # 選択されたとき
    #     for index in selected.indexes():
    #         # ここで直接self._wordColorを書き換えても表示は変わらない
    #         # setData関数を使う必要がある
    #         # setDataの引数には、index, isSelected,  QtCore.Qt.ForegroundRoleを渡す
    #         self.setData(index, True, QtCore.Qt.ForegroundRole)
# 夜勤表
class nightshiftDialog(QtWidgets.QDialog):

    def __init__(self, yakinModel: Model, shiftChannel: ShiftChannel, parent=None):
        # def __init__(self, shiftChannel, parent=None):
        super(nightshiftDialog, self).__init__(parent)
        self.shiftChannel = shiftChannel
        self.model = yakinModel
        self.initui()
        # self.doubleClickObj = None

    def initui(self):
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.view.setFont(font)

        #　ダブルクリックしたときのイベントを設定
        self.view.doubleClicked.connect(self.dclickevent)

        self.view.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.view.model().dataChanged.connect(self.onDataChanged)
        
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    # 右クリックしたときのイベント設定
    def contextMenuEvent(self, event):
        # 右クリックされた位置を取得し、その位置にメニューを表示
        pos = self.getEventPos(event.pos())
        selectedIndex = self.view.selectionModel().selectedIndexes()
        if len(selectedIndex) != 1:
            return None
        index = selectedIndex[0]
        if index.isValid():
            menu = QMenu(self)
            action = QAction('交代スタッフを探す')
 
            action.triggered.connect(lambda:self.onContextMenuActionTriggered(index))
            menu.addAction(action)
            menu.exec_(self.mapToGlobal(pos))

    # def showContextMenu(self, index, pos):

    #     print(f'{index.row()}____{index.column()}')
    #     if index.isValid():
    #         menu = QMenu(self)
    #         action = QAction('交代スタッフを探す')
 
    #         action.triggered.connect(lambda:self.onContextMenuActionTriggered(index))
    #         menu.addAction(action)
    #         menu.exec_(self.mapToGlobal(pos))

    def getEventPos(self, pos: QtCore.QPoint):
        # ヘッダーの高さを考慮して位置を取得する
        headerHeight = self.view.verticalHeader().defaultSectionSize()
        headerWidth = self.view.horizontalHeader().defaultSectionSize()
        pos.setX(pos.x()-headerWidth)
        pos.setY(pos.y()-headerHeight)

        return pos
    
    def onContextMenuActionTriggered(self, index):

        self.candidate = CandidateWidget(self.shiftChannel, self.model, index)
        self.candidate.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.candidate.show()

    def onSelectionChanged(self, selected, deselected):

        for ix in deselected.indexes(): 
            self.setFontColor(ix, QColor('#000000'), False)      

        for ix in selected.indexes():
            self.setFontColor(ix, QColor('#FFA500'), True) 

        self.view.viewport().update()

    def setFontColor(self, index, color: QColor, fontFlg):
            textColorList = self.model.textColorGen(index)
            for row, col in textColorList:
                index = self.model.index(row, col, QtCore.QModelIndex())
                self.model.setData(index, color, QtCore.Qt.ForegroundRole)
                self.model.setData(index, fontFlg, QtCore.Qt.FontRole)       

    def onDataChanged(self, index):
        #一括で_textColor，_fontを初期化する
        self.model._textColor.values[:] = QColor('#000000')
        self.model._font.values[:] = False

        self.setFontColor(index, QColor('#FFA500'), True) 

        self.view.viewport().update()

    def dclickevent(self, item):

    # ダブルクリックしたデータを編集できるか判定する　⇒　DummyPlaceかどうか
        # if (item.row(), item.column()) in self.model.DummyPlace:
        self.candidate = CandidateWidget(self.shiftChannel, self.model, item)
        self.candidate.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.candidate.show()

    def fn_get_cell_Value(self, index):
        datas = index.data()


'''
src = csvファイルを読み込んで成形したデータ
nightModel = nightshiftdialogで使用しているモデル
nightIndex = nightshiftdialogで使用しているモデルのインデックス
'''

#LOGPATH = pathlib.Path("C://Users//pelu0//PycharmProjects//ShiftManagerGitHub//work//integral//log")


class CandidateWidget(QtWidgets.QWidget):

    def __init__(self, shiftChannel: ShiftChannel, nightModel: Model, nightIndex: QtCore.QModelIndex, parent=None):
        super().__init__(parent)

        self.nightshiftModel = nightModel
        self.nightshiftModelIndex = nightIndex
        self.rk = shiftChannel.shiftCtrl.rk
        self.dfskill = shiftChannel.shiftCtrl.getDFSkill()
        self.DFrenzoku = shiftChannel.shiftCtrl.getDFRenzoku()
        self.DFshift = shiftChannel.shiftCtrl.getDFShift()
        #self.DFkinmuhyou = shiftChannel.shiftCtrl.getDFKinmuOnly()
        self.DFkinmuhyou_long = shiftChannel.shiftCtrl.getDFKinmuFull()
        self.DFstaff = shiftChannel.shiftCtrl.getDFstaff()
        self.DFNrdeptcore = shiftChannel.shiftCtrl.getNrdeptcore(DataName.DFNrdept)
        self.RawDFNrdeptcore = shiftChannel.shiftCtrl.getNrdeptcore(DataName.RawDFNrdeptcore)
        # コアメンバーは辞書型で取得する
        #self.DictCore = shiftChannel.shiftCtrl.getNrdeptcore(DataName.DFCore)
        self.targetRow = nightIndex.row() + int(self.rk)
        self.targetColumn = nightIndex.column()
        self.targetData = nightIndex.data()
        self._kinmu = shiftChannel.shiftCtrl.getKinmuForm(DataName.kinmu)
        self._previous = shiftChannel.shiftCtrl.getKinmuForm(DataName.previous)
        self._request = shiftChannel.shiftCtrl.getKinmuForm(DataName.request)
        self._data = pd.DataFrame(data=[['' for j in range(len(self._kinmu.columns))] for i in range(len(self._kinmu))],
                                  index=self._kinmu.index.values.tolist(),
                                  columns=self._kinmu.columns.values.tolist())
        self._JapanHoliday = shiftChannel.shiftCtrl.getJapanHolidayDF()
        self.createDF()

        "=============================log========================================="
        # self.dfskill.to_csv(LOGPATH/'dfskill.csv')
        # self.DFrenzoku.to_csv(LOGPATH/'DFrenzoku.csv')
        # self.DFshift.to_csv(LOGPATH/'DFshift.csv')
        # self.DFkinmuhyou.to_csv(LOGPATH/'DFkinmuhyou.csv')
        # self.DFkinmuhyou_long.to_csv(LOGPATH/'DFkinmuhyou_long.csv')
        # self.DFstaff.to_csv(LOGPATH/'DFstaff.csv')
        # self.DFNrdeptcore.to_csv(LOGPATH/'DFNrdeptcore.csv')
        # self.RawDFNrdeptcore.to_csv(LOGPATH/'RawDFNrdeptcore.csv')
        "=============================log========================================="

        self.data = self.createCandidate()
        self.model = CandidateModel(self.data)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.view.doubleClicked.connect(self.dclickevent)
        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)


    def dclickevent(self, index):
        # # 編集時のダブルクリックイベント

        row = index.row()
        selected = self.createCandidate().iat[index.row(), index.column()]
        parentRow = self.nightshiftModelIndex.row()
        parentCol = self.nightshiftModelIndex.column()
        idx = self.model.index(row, 0, QtCore.QModelIndex())
        staff = self.model.data(idx, QtCore.Qt.DisplayRole)
        job = self.nightshiftModelIndex.model().headerData(parentCol, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        date = self.nightshiftModelIndex.model().headerData(parentRow, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)
        self.nightshiftModel.setData(self.nightshiftModelIndex, staff, QtCore.Qt.EditRole)
        

        self.close()

    '''
    候補者レコード = '氏名','休日','連続勤務回数','夜勤回数','日直回数' を出力
    '''

    # 空白のみ候補者
    def createDF(self):
        for i in range(len(self._data)):
            for j in range(len(self._data.columns)):
                value = self._kinmu.iat[i, j]
                request = self._request.iat[i, j]
                if request is not None:
                    value = request
                elif value == '勤':
                    value = None
                elif value == '休':
                    value = None
                self._data.iat[i, j] = value

    def createCandidate(self):
        # ダブルクリックしたセルから日付を取得
        targetDayS = self.targetRow
        targetDayE = targetDayS + 1
        # 休診日
        # self.columnslist[index.column()] in self._closed
        # 取得した日付で勤務表を成形
        DFTargetDaysJob = self._data.iloc[:, [targetDayS, targetDayE]]
        # カラム[UID]を追加
        DFTargetDaysJob['UID'] = self._data.index.values.copy()
        # 勤務が休・勤以外は消去する
        DFTargetDayStartJob = DFTargetDaysJob.iloc[:, [0, 2]]
        DFTargetDayStartJob = DFTargetDayStartJob[DFTargetDayStartJob.iloc[:, 0].isnull()]
        DFTargetDayEndJob = DFTargetDaysJob.iloc[:, [1, 2]]
        DFTargetDayEndJob = DFTargetDayEndJob[DFTargetDayEndJob.iloc[:, 0].isnull()]
        DFKouho = pd.merge(DFTargetDayStartJob, DFTargetDayEndJob, on="UID", how='inner')
        DFCore = pd.DataFrame(data=self.RawDFNrdeptcore)
        DFSkill = pd.concat([DFCore, self.dfskill], axis=1)
        DFSkill['UID'] = DFSkill.index.values

        # 担当勤務による絞り込み
        if self.targetColumn == 0:
            DFJobKouho = DFSkill[(DFSkill["A夜"] == '2') & (DFSkill["夜勤"] == '2')]
        elif self.targetColumn == 1:
            DFJobKouho = DFSkill[(DFSkill['M夜'] == '2') & (DFSkill['夜勤'] == '2')]
        elif self.targetColumn == 2:
            DFJobKouho = DFSkill[(DFSkill['C夜'] == '2') & (DFSkill['夜勤'] == '2')]
        elif self.targetColumn == 3:
            DFJobKouho = DFSkill[(DFSkill["A夜"] == '2') & (DFSkill["日勤"] == '2')]
        elif self.targetColumn == 4:
            DFJobKouho = DFSkill[(DFSkill['M夜'] == '2') & (DFSkill['日勤'] == '2')]
        elif self.targetColumn == 5:
            DFJobKouho = DFSkill[(DFSkill['C夜'] == '2') & (DFSkill['日勤'] == '2')]
        elif self.targetColumn == 6 or 7:
            DFJobKouho = DFSkill[DFSkill['日勤'] == '2']
        DFJobKouho = pd.merge(DFKouho, DFJobKouho, on="UID", how='inner')
        DFJobKouho = DFJobKouho.iloc[:, [0, 1, 2, 3]]
        DFJobKouho1 = DFJobKouho.reindex(columns=['UID', 'Mo', DFJobKouho.columns[0], DFJobKouho.columns[2]])

        # コアメンバーの確認(勤務しているコアの数)
        DFRtCoreNo = DFSkill[(DFSkill['Mo'] == 'RT') & (DFSkill['RT'] == '6')]
        DFMRCoreNo = DFSkill[(DFSkill['Mo'] == 'MR') & (DFSkill['MR'] == '6')]
        DFTVCoreNo = DFSkill[(DFSkill['Mo'] == 'TV') & (DFSkill['TV'] == '6')]
        DFKSCoreNo = DFSkill[(DFSkill['Mo'] == 'KS') & (DFSkill['KS'] == '6')]
        DFNMCoreNo = DFSkill[(DFSkill['Mo'] == 'NM') & (DFSkill['NM'] == '6')]
        DFXPCoreNo = DFSkill[(DFSkill['Mo'] == 'XP') & (DFSkill['XP'] == '6')]
        DFCTCoreNo = DFSkill[(DFSkill['Mo'] == 'CT') & (DFSkill['CT'] == '6')]
        DFXOCoreNo = DFSkill[(DFSkill['Mo'] == 'XO') & (DFSkill['XO'] == '6')]
        DFAGCoreNo = DFSkill[(DFSkill['Mo'] == 'AG') & (DFSkill['AG'] == '6')]
        DFMGCoreNo = DFSkill[(DFSkill['Mo'] == 'MG') & (DFSkill['MG'] == '6')]
        DFMTCoreNo = DFSkill[(DFSkill['Mo'] == 'MT') & (DFSkill['MT'] == '6')]

        # 候補日のコアメンバーの計算
        # 入り・日直
        DFTargetDayStartCoreNo = DFTargetDaysJob.iloc[:, [0, 2]]
        DFTargetDayStartCoreNo = DFTargetDayStartCoreNo[(DFTargetDayStartCoreNo.iloc[:, 0] == "勤")]
        # RTコア数
        DFTargetDayStartRTCoreNo = pd.merge(DFTargetDayStartCoreNo, DFRtCoreNo, on="UID", how='inner')
        # MRコア数
        DFTargetDayStartMRCoreNo = pd.merge(DFTargetDayStartCoreNo, DFMRCoreNo, on="UID", how='inner')
        # TVコア数
        DFTargetDayStartTVCoreNo = pd.merge(DFTargetDayStartCoreNo, DFTVCoreNo, on="UID", how='inner')
        # KSコア数
        DFTargetDayStartKSCoreNo = pd.merge(DFTargetDayStartCoreNo, DFKSCoreNo, on="UID", how='inner')
        # NMコア数
        DFTargetDayStartNMCoreNo = pd.merge(DFTargetDayStartCoreNo, DFNMCoreNo, on="UID", how='inner')
        # XP
        DFTargetDayStartXPCoreNo = pd.merge(DFTargetDayStartCoreNo, DFXPCoreNo, on="UID", how='inner')
        # CT
        DFTargetDayStartCTCoreNo = pd.merge(DFTargetDayStartCoreNo, DFCTCoreNo, on="UID", how='inner')
        # XO
        DFTargetDayStartXOCoreNo = pd.merge(DFTargetDayStartCoreNo, DFXOCoreNo, on="UID", how='inner')
        # AG
        DFTargetDayStartAGCoreNo = pd.merge(DFTargetDayStartCoreNo, DFAGCoreNo, on="UID", how='inner')
        # MG
        DFTargetDayStartMGCoreNo = pd.merge(DFTargetDayStartCoreNo, DFMGCoreNo, on="UID", how='inner')
        # MT
        DFTargetDayStartMTCoreNo = pd.merge(DFTargetDayStartCoreNo, DFMTCoreNo, on="UID", how='inner')

        # 明
        DFTargetDayEndCoreNo = DFTargetDaysJob.iloc[:, [1, 2]]
        DFTargetDayEndCoreNo = DFTargetDayEndCoreNo[(DFTargetDayEndCoreNo.iloc[:, 0] == "勤")]
        # RTコア数
        DFTargetDayEndRTCoreNo = pd.merge(DFTargetDayEndCoreNo, DFRtCoreNo, on="UID", how='inner')
        # XOコア数
        DFTargetDayEndMRCoreNo = pd.merge(DFTargetDayEndCoreNo, DFMRCoreNo, on="UID", how='inner')
        # TVコア数
        DFTargetDayEndTVCoreNo = pd.merge(DFTargetDayEndCoreNo, DFTVCoreNo, on="UID", how='inner')
        # KSコア数
        DFTargetDayEndKSCoreNo = pd.merge(DFTargetDayEndCoreNo, DFKSCoreNo, on="UID", how='inner')
        # NMコア数
        DFTargetDayEndNMCoreNo = pd.merge(DFTargetDayEndCoreNo, DFNMCoreNo, on="UID", how='inner')
        # XP
        DFTargetDayEndXPCoreNo = pd.merge(DFTargetDayEndCoreNo, DFXPCoreNo, on="UID", how='inner')
        # CT
        DFTargetDayEndCTCoreNo = pd.merge(DFTargetDayEndCoreNo, DFCTCoreNo, on="UID", how='inner')
        # XO
        DFTargetDayEndXOCoreNo = pd.merge(DFTargetDayEndCoreNo, DFXOCoreNo, on="UID", how='inner')
        # AG
        DFTargetDayEndAGCoreNo = pd.merge(DFTargetDayEndCoreNo, DFAGCoreNo, on="UID", how='inner')
        # MG
        DFTargetDayEndMGCoreNo = pd.merge(DFTargetDayEndCoreNo, DFMGCoreNo, on="UID", how='inner')
        # MT
        DFTargetDayEndMTCoreNo = pd.merge(DFTargetDayEndCoreNo, DFMTCoreNo, on="UID", how='inner')

        # 勤務候補者へコア数追加
        # 夜勤の場合
        if self.targetColumn == 0 or self.targetColumn == 1 or self.targetColumn == 2:
            # コア格納列追加
            for i in range(len(DFJobKouho1)):
                if DFJobKouho1.iloc[i, 1] == 'RT':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartRTCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndRTCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'MR':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartMRCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndMRCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'TV':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartTVCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndTVCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'KS':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartKSCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndKSCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'NM':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartNMCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndNMCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'XP':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartXPCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndXPCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'CT':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartCTCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndCTCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'XO':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartXOCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndXOCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'AG':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartAGCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndAGCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'MG':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartMGCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndMGCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'MT':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartMTCoreNo)
                    DFJobKouho1.iloc[i, 3] = len(DFTargetDayEndMTCoreNo)
        # 日勤の場合
        else:
            # コア格納列追加
            for i in range(len(DFJobKouho1)):
                if DFJobKouho1.iloc[i, 1] == 'RT':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartRTCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'MR':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartMRCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'TV':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartTVCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'KS':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartKSCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'NM':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartNMCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'XP':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartXPCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'CT':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartCTCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'XO':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartXOCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'AG':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartAGCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'MG':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartMGCoreNo)
                elif DFJobKouho1.iloc[i, 1] == 'MT':
                    DFJobKouho1.iloc[i, 2] = len(DFTargetDayStartMTCoreNo)

        # 空のDF作成
        DFCount = pd.DataFrame(index=DFJobKouho1["UID"].values.tolist(), columns=['休日', '夜勤回数', "日直回数"])
        DFCount["UID"] = DFJobKouho1["UID"].values.tolist()

        # 休日の過不足　値 in リスト
        # 夜勤の場合
        a = 0
        b = 0
        c = 0
        if self.targetColumn == 0 or self.targetColumn == 1 or self.targetColumn == 2:
            if DFJobKouho1.columns.values.tolist()[2] in self._JapanHoliday:
                a = -1
            if DFJobKouho1.columns.values.tolist()[3] in self._JapanHoliday:
                b = -1
            c = a + b
        else:
            if DFJobKouho1.columns.values.tolist()[2] in self._JapanHoliday:
                a = -1
            c = a

        for item in DFCount["UID"]:
            # 休日計算(休日の過不足)
            # DFCount.at[item, '休日'] = ((self.DFshift["Job"] == '10') & (self.DFshift.index == item) | (self.DFshift["Job"] == '50') & (self.DFshift.index == item)).values.sum()
            DFCount.at[item, '休日'] = c

            # 日直夜勤の数
            if self.targetColumn == 0 or self.targetColumn == 1 or self.targetColumn == 2:
                DFCount.at[item, '夜勤回数'] = ((self.DFshift["Job"] == '4') & (self.DFshift.index == item) | (
                            self.DFshift["Job"] == '5') & (self.DFshift.index == item) | (
                                                        self.DFshift["Job"] == '6') & (
                                                        self.DFshift.index == item)).values.sum() + 1
                DFCount.at[item, '日直回数'] = ((self.DFshift["Job"] == '0') & (self.DFshift.index == item) | (
                            self.DFshift["Job"] == '1') & (self.DFshift.index == item) | (
                                                        self.DFshift["Job"] == '2') & (self.DFshift.index == item) | (
                                                        self.DFshift["Job"] == '3') & (
                                                        self.DFshift.index == item)).values.sum()
            else:
                DFCount.at[item, '夜勤回数'] = ((self.DFshift["Job"] == '4') & (self.DFshift.index == item) | (
                            self.DFshift["Job"] == '5') & (self.DFshift.index == item) | (
                                                        self.DFshift["Job"] == '6') & (
                                                        self.DFshift.index == item)).values.sum()
                DFCount.at[item, '日直回数'] = ((self.DFshift["Job"] == '0') & (self.DFshift.index == item) | (
                            self.DFshift["Job"] == '1') & (self.DFshift.index == item) | (
                                                        self.DFshift["Job"] == '2') & (self.DFshift.index == item) | (
                                                        self.DFshift["Job"] == '3') & (
                                                        self.DFshift.index == item)).values.sum() + 1

        # 連続勤務
        # 連続勤務日計算
        # 勤務以外をNoneへ
        renkin = self.DFkinmuhyou_long.loc[DFJobKouho1["UID"].values.tolist()]
        DFRenkin = renkin.replace(['休', '振', '年', '夏', '特', '暇'], None)
        # 勤務を1へ
        DFRenkin = DFRenkin.replace(['勤', '出', '半', 'A夜', 'M夜', 'C夜', '明', 'A日', 'M日', 'C日', 'F日'], '1')
        # 夜勤入り明へ１
        if self.targetColumn == 0 or self.targetColumn == 1 or self.targetColumn == 2:
            DFRenkin.loc[:, DFJobKouho1.columns[2]] = '1'
            DFRenkin.loc[:, DFJobKouho1.columns[3]] = '1'
        else:
            DFRenkin.loc[:, DFJobKouho1.columns[2]] = '1'

        DFRenkinT = DFRenkin.T  # 転置
        # 空のDF
        DF = pd.DataFrame(index=DFJobKouho1["UID"].values.tolist(), columns=['連続勤務回数'])
        for item in DFRenkinT.columns:  # 遅い
            y = DFRenkinT.loc[:, item]
            # 対象列の連続する値を累積和を求める
            DFRenkinT['new'] = y.groupby((y != y.shift()).cumsum()).cumcount() + 1
            DF.loc[item, ['連続勤務回数']] = DFRenkinT['new'].max()
        # 休み等の回数+連続勤務回数
        DFCountAll = pd.concat([DFCount, DF], axis=1)
        # 候補者+休み等の回数+連続勤務回数
        DFKouhoSya = pd.merge(DFJobKouho1, DFCountAll, on="UID", how='inner')
        # 並べ替え
        # DFKouhoSya = DFKouhoSya.reindex(columns=['UID','Mo', targetDayS,  'Core', targetDayE, 'Core1', '休日', '連続勤務回数', '夜勤回数', '日直回数'])
        # DFkinmuhyou_longE.columns[0] + " Core"
        DFstaff = self.DFstaff
        DFKouhoSya = DFKouhoSya.rename(
            columns={DFKouhoSya.columns.values[2]: DFKouhoSya.columns.values[2] + '\n Core人数',
                     DFKouhoSya.columns.values[3]: DFKouhoSya.columns.values[3] + '\n Core人数'})
        DFSkillorg = DFSkill.copy()
        DFSkillorg.drop(columns=['Mo', 'A夜', 'M夜', 'C夜', 'F', '夜勤', '日勤'], inplace=True)
        DFKouhoSya = pd.merge(DFKouhoSya, DFSkillorg, on="UID", how='inner')

        for i in range(len(DFKouhoSya)):
            Mo = DFKouhoSya.iloc[i, 1]
            if self.targetColumn == 0 or self.targetColumn == 1 or self.targetColumn == 2:
                if DFKouhoSya[Mo][i] == '6':
                    DFKouhoSya.iat[i, 2] = DFKouhoSya.iat[i, 2] - 1
                    if DFKouhoSya.iat[i, 2] <= 0:
                        DFKouhoSya.iat[i, 2] = 0
                    DFKouhoSya.iat[i, 3] = DFKouhoSya.iat[i, 3] - 1
                    if DFKouhoSya.iat[i, 3] <= 0:
                        DFKouhoSya.iat[i, 3] = 0

        DFKouhoSya = DFKouhoSya.iloc[:, 0:8]

        # UID4Name
        for i in range(len(DFstaff)):
            for j in range(len(DFKouhoSya)):
                if DFstaff.iat[i, 0] == DFKouhoSya.iat[j, 0]:
                    DFKouhoSya.iat[j, 0] = DFstaff.iat[i, 2]

        if self.targetColumn == 0 or self.targetColumn == 1 or self.targetColumn == 2:
            pass
        else:
            DFKouhoSya.drop(DFKouhoSya.columns[[2, 3]], axis=1, inplace=True)

        a = DFJobKouho1.columns.values.tolist()[3]
        b = DFJobKouho1.columns.values.tolist()[2]

        if a in self._JapanHoliday:
            DFKouhoSya.drop(DFKouhoSya.columns[[3]], axis=1, inplace=True)
        if b in self._JapanHoliday:
            DFKouhoSya.drop(DFKouhoSya.columns[[2]], axis=1, inplace=True)

        return DFKouhoSya
