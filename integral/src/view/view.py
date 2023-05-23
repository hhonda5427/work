import pandas as pd
import datetime

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, QSize
from PyQt5.QtGui import QColor, QResizeEvent, QFont, QStandardItem, QShowEvent
from PyQt5.QtWidgets import (QTableView, QWidget, QAbstractItemView, 
                            QGridLayout, QHBoxLayout, QSizePolicy, QAbstractScrollArea, QComboBox,
                            QStyledItemDelegate, QLabel)

from util.dataSender import DataName
from util.shiftController import ShiftChannel
from util.kinnmuCount import *

ROWHEIGHT = 15
COLUMNWIDTH = 15


shiftColors = {'A夜':QColor('#7FFFD4'), 'M夜':QColor('#7FFFD4'), 'C夜':QColor('#7FFFD4'),'明':QColor('#00FF00'), 
               'A日':QColor('#FFFF00'), 'M日':QColor('#FFFF00'), 'C日':QColor('#FFFF00'), 'F日':QColor('#FFFF00'),
               '勤':QColor('#00000000'), '張':QColor('#9400D3'),
               '休':QColor('#B2B2B2'), '年':QColor('#FFC0CB'), '特':QColor('#D2691E'), '夏':QColor('#F4A460'), '半':QColor('#FFDAB9'),
                None:QColor('#00000000'), '':QColor('#00000000')}

modalityColors = {'RT':QColor('#99ccff'), 'MR':QColor('#99FFFF'), 'TV':QColor('#00FFFF'), 
                  'KS':QColor('#99FFFF'), 'NM':QColor('#00FFCC'), 'XP':QColor('#FF9933'), 
                  'CT':QColor('#FFCC66'), 'XO':QColor('#9999FF'), 'AG':QColor('#669933'),
                  'FR':QColor('#F5F5F5'), 'AS':QColor('#D3D3D3'), 'ET':QColor('#A9A9A9')}

class ShiftTableWidget(QWidget):
    def __init__(self, shiftModel, rowHeaderModel, columnHeaderModel, countModel):
        QWidget.__init__(self)

        self.rowHeaderModel = rowHeaderModel
        self.columnHeaderModel = columnHeaderModel
        self.shiftModel = shiftModel
        self.countModel = countModel

        self.columnHeaderView = BaseView()
        self.columnHeaderView.setModel(self.columnHeaderModel)
        self.columnHeaderView.horizontalScrollBar().valueChanged.connect(self.SyncHorizontalScrollBar)

        self.rowHeaderView = BaseView()
        self.rowHeaderView.setModel(self.rowHeaderModel)
        self.rowHeaderView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        
        self.shiftView = BaseView()
        self.shiftView.setModel(self.shiftModel)
        self.shiftView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        self.shiftView.horizontalScrollBar().valueChanged.connect(self.SyncHorizontalScrollBar)
        self.shiftView.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.shiftView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shiftView.setEditTriggers(QAbstractItemView.CurrentChanged)
        self.shiftView.setItemDelegate(ShiftDelegate())
        self.shiftView.model().dataChanged.connect(self.onDataChanged)

        self.scrollView = BaseView()
        self.scrollView.hide()
        self.scrollView.setModel(self.shiftModel)
        self.scrollView.horizontalScrollBar().valueChanged.connect(self.SyncHorizontalScrollBar)
        self.scrollView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        self.scrollView.viewport().stackUnder(self.shiftView)

        self.countView = BaseView()
        self.countView.setModel(self.countModel)
        self.countView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        
        titleHeader = QWidget()
        titleHeader.setLayout(QHBoxLayout())
        date = datetime.datetime.strptime(shiftModel.shiftCtrlChannel.shiftCtrl.toHeader_nowMonth()[0], '%Y-%m-%d')
        titleLabel = QLabel(date.strftime('%Y/%m'))
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        titleLabel.setFont(font)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleHeader.layout().addWidget(titleLabel)
        
        countHeader = QWidget()
        countHeader.setLayout(QHBoxLayout())
        label1 = QLabel("連")
        label2 = QLabel("休")
        label1.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        label2.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        countHeader.layout().addWidget(label1)
        countHeader.layout().addWidget(label2)

        self.baseLayout = QGridLayout()
        self.baseLayout.setHorizontalSpacing(0)
        self.baseLayout.setVerticalSpacing(0)
        self.baseLayout.setContentsMargins(0, 0, 0, 0)

        self.baseLayout.addWidget(self.columnHeaderView, 0, 1)
        self.baseLayout.addWidget(self.rowHeaderView, 1, 0)
        self.baseLayout.addWidget(self.scrollView, 1, 1)
        self.baseLayout.addWidget(self.shiftView, 1, 1)
        self.baseLayout.addWidget(self.scrollView.horizontalScrollBar(), 2, 1)
        self.baseLayout.addWidget(self.countView, 1, 2)
        self.baseLayout.addWidget(self.scrollView.verticalScrollBar(), 1, 3)
        self.baseLayout.addWidget(titleHeader, 0,0)
        self.baseLayout.addWidget(countHeader, 0,2)

        
        self.setColumnWidth()
        self.setRowHeight()

        self.setLayout(self.baseLayout)
        self.setContentsMargins(5, 0, 0, 0)
        self.setMinimumSize(1000, 400)

# ---------------------------------------------------------------

        data=self.shiftView.model()._data
        
        iota =  int(*shiftModel.shiftCtrlChannel.shiftCtrl.config['iota'])
   
        #・・・連続勤務日数の計算・・・
        columss=len(data.index)
        colum2=len(data.columns)
        tail=colum2-1#変更された行の今月分のみ取得#今月分データ
        data2=data.iloc[:,:tail]

        self.init_count_func_con(data, iota, columss, colum2, tail, data2)

    def init_count_func_con(self, data, iota, columss, colum2, tail, data2):
        for z in range(columss):
            # l.clear()
            data4 = data.iloc[z,iota:tail]
            kyu=(data4=='休').sum()

            #最大連続勤務日数の計算
            mwork = count_consecutive_workdays(data2, z, tail) 

            index = self.countView.model().index(z, 0,QModelIndex())
            index2 = self.countView.model().index(z, 1,QModelIndex())
            self.countView.model().setData(index2, kyu, Qt.EditRole)         
            self.countView.model().setData(index, mwork, Qt.EditRole)

        for i in range(colum2):
            data5=data.iloc[:,i]
            data6=data5.T
            kyu2=(data6=='休').sum()
            #print(data6)
            index3 = self.columnHeaderView.model().index(0,i,QModelIndex())
            self.columnHeaderView.model().setData(index3,kyu2,Qt.EditRole)
    
        #data2.to_csv("kinmucount.csv",encoding="Shift-JIS")
          
    def setColumnWidth(self):
        staffwidth = [100, 30]
        ncol = self.shiftModel.columnCount()

        for col in range(ncol):
            self.columnHeaderView.horizontalHeader().resizeSection(col, COLUMNWIDTH)
            self.shiftView.horizontalHeader().resizeSection(col, COLUMNWIDTH)
            self.scrollView.horizontalHeader().resizeSection(col, COLUMNWIDTH)
            if col < self.rowHeaderModel.columnCount():
                self.rowHeaderView.horizontalHeader().resizeSection(col, staffwidth[col])
            if col < self.countModel.columnCount():
                self.countView.horizontalHeader().resizeSection(col, COLUMNWIDTH)   
    
    def setRowHeight(self):
        
        nrow = self.rowHeaderModel.rowCount()
        for row in range(nrow):
            self.rowHeaderView.verticalHeader().resizeSection(row, ROWHEIGHT)
            self.countView.verticalHeader().resizeSection(row, ROWHEIGHT)
            self.shiftView.verticalHeader().resizeSection(row, ROWHEIGHT)
            self.scrollView.verticalHeader().resizeSection(row, ROWHEIGHT)

            if row < self.columnHeaderModel.rowCount():
                self.columnHeaderView.verticalHeader().resizeSection(row, ROWHEIGHT)


    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        maxval = self.shiftView.horizontalScrollBar().maximum()
        self.scrollView.horizontalScrollBar().setMaximum(maxval)
        
        maxval = self.shiftView.verticalScrollBar().maximum()
        self.scrollView.verticalScrollBar().setMaximum(maxval)
        
    def showEvent(self, a0:QShowEvent) -> None:
        super().showEvent(a0)
        


    def SyncHorizontalScrollBar(self, value):
        
        self.shiftView.horizontalScrollBar().setValue(value)
        self.columnHeaderView.horizontalScrollBar().setValue(value)
        self.scrollView.horizontalScrollBar().setValue(value)

    def SyncVerticalScrollBar(self, value):
        
        self.shiftView.verticalScrollBar().setValue(value)
        self.rowHeaderView.verticalScrollBar().setValue(value)
        self.countView.verticalScrollBar().setValue(value)
        self.scrollView.verticalScrollBar().setValue(value)

    def onSelectionChanged(self, selected, deselected):
        cols = self.rowHeaderView.model().columnCount()
        rows = self.columnHeaderView.model().rowCount()
        for ix in deselected.indexes():
            for col in range(cols):
                index = self.rowHeaderView.model().index(ix.row(), col ,QModelIndex())
                self.rowHeaderView.model().setData(index, False, Qt.FontRole)                
            for row in range(rows):
                index = self.columnHeaderView.model().index(row, ix.column(), QModelIndex())
                self.columnHeaderView.model().setData(index, False, Qt.FontRole)
        for ix in selected.indexes():
            # emphasize column,row header 
            for col in range(cols):
                index = self.rowHeaderView.model().index(ix.row(), col ,QModelIndex())
                self.rowHeaderView.model().setData(index, True, Qt.FontRole)
            for row in range(rows):
                index = self.columnHeaderView.model().index(row, ix.column(), QModelIndex())
                self.columnHeaderView.model().setData(index, True, Qt.FontRole)

    def onDataChanged(self, index):  
        '''
        ここに休日などをカウントする関数を記述する
        '''

        row = index.row()
        column = index.column()
        data = self.shiftView.model()._data.iloc[index.row(), :]
        uid = self.shiftView.model().headerData(row, Qt.Vertical, Qt.DisplayRole)
        date = self.shiftView.model().headerData(column, Qt.Horizontal, Qt.DisplayRole)
        
        shiftModel : ShiftModel = self.shiftView.model()
        #連続勤務日数　基準日より何日前か
        #*がわからない場合はリストのアンパッキングで検索してください
        iota =  int(*shiftModel.shiftCtrlChannel.shiftCtrl.config['iota'])

        data = self.shiftView.model()._data#全体データフレーム
        # print(f'{row}___{column}__{data}__{uid}___{date}')
        # print(row)
        # print(column)
        #rowa=int(row)
        conwork = count_this_row(data,row,iota, want_to_count=ShiftElement.HOLIDAY)
        conworkcol=countfunc_col(data,column)
        index = self.countView.model().index(index.row(), 0,QModelIndex())
        index2 = self.countView.model().index(index.row(), 1,QModelIndex())
        index3 = self.columnHeaderView.model().index(0,column,QModelIndex())
        self.countView.model().setData(index, conwork[0], Qt.EditRole)
        self.countView.model().setData(index2, conwork[1], Qt.EditRole)
        self.columnHeaderView.model().setData(index3,conworkcol,Qt.EditRole)
        self.countView.viewport().update()
        self.columnHeaderView.viewport().update()

class BaseView(QTableView):

    def __init__(self, parent=None, *args):
        super().__init__()
        
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        font = QFont()
        font.setPointSize(8)
        self.setFont(font)
        

class TableModel(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super().__init__()

        self._data = None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column, QModelIndex())

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._data)
        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._data.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data.iat[index.row(), index.column()])
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter 
        return None

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

        return None 

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data.iat[index.row(), index.column()] = value
            return True
        return False    

class RowHeaderModel(TableModel):
    def __init__(self, shiftChannel:ShiftChannel, parent=None, *args):
        super().__init__(self, parent, *args)
        self._data = shiftChannel.shiftCtrl.getStaffInfo()
        self._font = [False for i in range(len(self._data))]
        self._color = [QColor('#00000000') for i in range(len(self._data))]

        self.setColor()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None
        value = self._data.iat[index.row(), index.column()]
        if role == Qt.DisplayRole:  
            return str(value)

        elif role == Qt.BackgroundRole:
            if index.column() == 1:
                return self._color[index.row()]

            return QColor('#00000000')
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter 
        elif role == Qt.FontRole:            
            font = QFont()   
            flg = self._font[index.row()]
            font.setBold(flg)
            font.setItalic(flg)
            return QVariant(font)
        elif role == Qt.SizeHintRole:
            return QSize(COLUMNWIDTH, ROWHEIGHT)
        
    def setData(self, index, value, role):
        
        if index.isValid():
            if role == Qt.FontRole:
                self._font[index.row()] = value
                self.dataChanged.emit(index, index)
                return True
            else:
                return False
        else:
            return False

    def setColor(self):

        for row in range(len(self._data)):
            dept = self._data.iat[row, 1]
            if dept in modalityColors:
                self._color[row] = modalityColors[dept]


class ColumnHeaderModel(TableModel):
    def __init__(self, shiftChannel:ShiftChannel, parent=None, *args):
        super().__init__(self, parent, *args)
        self._data = shiftChannel.shiftCtrl.getCalendarDF()
        self._closed = shiftChannel.shiftCtrl.getJapanHolidayDF()
        self.columnslist = self._data.columns.values
        self._font = [False for i in range(len(self._data.columns))]

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])

        elif role == Qt.BackgroundRole and index.row() != 0:
            if self.columnslist[index.column()] in self._closed:
                return QColor('#B2B2B2')
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter 
        
        elif role == Qt.FontRole:            
            font = QFont()   
            flg = self._font[index.column()]
            font.setBold(flg)
            font.setItalic(flg)
            return QVariant(font)
        
        elif role == Qt.SizeHintRole:
            return QSize(COLUMNWIDTH, ROWHEIGHT)
        
    def setData(self, index, value, role):
        
        if index.isValid():
            if role == Qt.FontRole:
            
                self._font[index.column()] = value
                self.dataChanged.emit(index, index)
                return True
            elif role == Qt.ItemDataRole.EditRole:
                self._data.iat[index.row(), index.column()] = value
            else:

                return False
        else:
            return False


class ShiftModel(TableModel):
    def __init__(self, shiftCtrlChannel: ShiftChannel, parent=None, *args):    
        super().__init__(self, parent, *args)
        self._kinmu = shiftCtrlChannel.shiftCtrl.getKinmuForm(DataName.kinmu)
        self._previous = shiftCtrlChannel.shiftCtrl.getKinmuForm(DataName.previous)
        self._request = shiftCtrlChannel.shiftCtrl.getKinmuForm(DataName.request)

        self.shiftCtrlChannel = shiftCtrlChannel

        self._data = pd.DataFrame(data=[['' for j in range(len(self._kinmu.columns))] for i in range(len(self._kinmu))],
                                         index=self._kinmu.index.values.tolist(), 
                                         columns=self._kinmu.columns.values.tolist())
        self._color = pd.DataFrame(data=[[QColor('#00000000') for j in range(len(self._data.columns))] for i in range(len(self._data))])
        self._textColor = pd.DataFrame(data=[[QColor('#00000000') for j in range(len(self._data.columns))] for i in range(len(self._data))])
        self.createDF()
        self.setBackgroundColors()
        self.setTextColors()
        
        # self._data.to_csv('C:\\Users\\unawa\\Documents\\ProgramSpace\\shiftManager\\work\\integral\\log\\kinmudata.csv')

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        value = self._data.iat[index.row(), index.column()]

        if role == Qt.DisplayRole:
            return value

        elif role == Qt.BackgroundRole:
            return self._color.iat[index.row(), index.column()]   

        elif role == Qt.TextColorRole:
            return self._textColor.iat[index.row(), index.column()]

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter 
        
        elif role == Qt.SizeHintRole:
            return QSize(COLUMNWIDTH, ROWHEIGHT)
        return None  

    def setData(self, index, value, role=Qt.EditRole):
        
        previous = self._previous.iat[index.row(), index.column()]
        request = self._request.iat[index.row(), index.column()]        
        if previous is not None or request is not None:
            return False

        if role == Qt.EditRole:
            
            self._data.iat[index.row(), index.column()] = value
            self._kinmu.iat[index.row(), index.column()] = value
            self._color.iat[index.row(), index.column()] = shiftColors[value]
            
            if value == '勤':
                self._data.iat[index.row(), index.column()] = None

            self.rewriteDatabase(index)

            self.dataChanged.emit(index, index)

            return True

        return False    

    def rewriteDatabase(self, index):
        # 名前からUIDを取得
        jobDict = {'休':'10', '勤':'8', '':'8', None:'8', 'A日':'0', 'M日':'1', 'C日':'2', 'F日':'3', 'A夜':'4', 'M夜':'5', 'C夜':'6', '明':'7'}
        uid = int(self.headerData(index.row(), Qt.Vertical, Qt.DisplayRole))
        strdate = self.headerData(index.column(), Qt.Horizontal, Qt.DisplayRole)
        # print(strdate)
        date = datetime.datetime.strptime(strdate, '%Y-%m-%d')
        datetuple = tuple([date.year, date.month, date.day])
        job = jobDict[self._data.iat[index.row(), index.column()]]

        self.shiftCtrlChannel.shiftCtrl.members[uid].jobPerDay[datetuple] = job


    def refreshData(self):
        self._kinmu = self.shiftCtrlChannel.shiftCtrl.getKinmuForm(DataName.kinmu)
        self.createDF()
        self.setBackgroundColors()


    def createDF(self):
        for i in range(len(self._data)):
            for j in range(len(self._data.columns)):        
                value = self._kinmu.iat[i, j]
                previous = self._previous.iat[i, j]
                request = self._request.iat[i, j]        
                if previous is not None:
                    value = previous
                elif request is not None:
                    value = request
                elif value == '勤':
                    value = None
                self._data.iat[i, j] = value


    # previous, request, shift に応じた文字カラーを設定
    def setTextColors(self):

        for i in range(len(self._data)):
            for j in range(len(self._data.columns)):
                    previous = self._previous.iat[i, j]
                    request = self._request.iat[i, j]
                    if previous is not None:
                        self._textColor.iat[i, j] = QColor('#808080')
                    elif request is not None:
                        self._textColor.iat[i, j] = QColor('#ff0000')
                    else:
                        self._textColor.iat[i, j] = QColor('#000000')

    # セルの色を設定
    def setBackgroundColors(self):
            
            for i in range(len(self._data)):
                for j in range(len(self._data.columns)):
                    shift = self._data.iat[i, j]
                    previous = self._previous.iat[i, j]
                    request = self._request.iat[i, j]
                    if previous is not None and previous in shiftColors:
                        self._color.iat[i,j] = shiftColors[previous]
                    elif request is not None and request in shiftColors:
                        self._color.iat[i, j] = shiftColors[request]
                    elif shift in shiftColors:
                        self._color.iat[i, j] = shiftColors[shift]
    
    # 対象のセルが前月分の勤務かあるいは希望勤務が存在するか判定する→delegateで
    def previous_request(self, index):
        previous = self._previous.iat[index.row(), index.column()]
        request = self._request.iat[index.row(), index.column()]

        if request is None and previous is None:

            return True
        else:

            return False

    def copy(self):
        return self._data.copy()

class ShiftDelegate(QStyledItemDelegate):
    
    def __init__(self, parent=None):
        super(ShiftDelegate, self).__init__(parent)
        self.initvalue = ''
        
    def createEditor(self, parent, option, index):
        if index.model().previous_request(index):
            editor = QComboBox()
            editor.setParent(parent)

            return editor
        else:
            return None

    def setEditorData(self, editor, index):
        shifts = ['休', '勤', 'A日', 'M日', 'C日', 'F日', 'A夜', 'M夜', 'C夜', '明']
        
        self.initvalue = index.model().data(index, Qt.DisplayRole)
        model = editor.model()       
        for item in shifts:
            stdItem = QStandardItem()
            stdItem.setBackground(shiftColors[item])    
            stdItem.setText(item)
            model.appendRow(stdItem)    
            # editor.addItem(stdItem)
        editor.setCurrentIndex(editor.findText(self.initvalue))

    def setModelData(self, editor, model, index):

        value = editor.currentText()
        # comboboxのindexを変更していれば　⇒　値を編集していればmodelのsetDataへ
        if not editor.currentIndex() < 0:
            model.setData(index, value, Qt.EditRole)

class CountModel(TableModel):
    def __init__(self, shiftCtrlChannel: ShiftChannel, parent=None, *args):
        super().__init__(self, parent, *args)
        uidIndex = shiftCtrlChannel.shiftCtrl.getStaffInfo().index.values.tolist()
        df = pd.DataFrame(index = uidIndex, columns= ['dayoff', 'consective'])
        df.fillna(0, inplace=True)
        self._data = df