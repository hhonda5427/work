import sys
import pandas as pd
import datamodel
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant
from PyQt5.QtGui import QColor, QResizeEvent, QFont, QStandardItem
from PyQt5.QtWidgets import (QTableView, QApplication, QWidget, QAbstractItemView, 
                            QGridLayout, QSizePolicy, QAbstractScrollArea, QComboBox,
                            QStyledItemDelegate)
ROWHEIGHT = 30
COLUMNWIDTH = 20


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
    def __init__(self):
        QWidget.__init__(self)

        data = datamodel.DataModel()
        
        self.rowHeaderModel = RowHeaderModel(data.staffinfo)
        self.columnHeaderModel = ColumnHeaderModel(data.header, data.closed)
        self.shiftModel = ShiftModel(data.shiftdf, data.previousdf, data.requestdf)
        self.countModel = CountModel(data.counttable)

        self.columnHeaderView = BaseView()
        self.columnHeaderView.setModel(self.columnHeaderModel)
        self.columnHeaderView.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.columnHeaderView.horizontalScrollBar().valueChanged.connect(self.SyncHorizontalScrollBar)

        self.rowHeaderView = BaseView()
        self.rowHeaderView.setModel(self.rowHeaderModel)
        self.rowHeaderView.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.rowHeaderView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        
        self.shiftView = BaseView()
        self.shiftView.setModel(self.shiftModel)
        self.shiftView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        self.shiftView.horizontalScrollBar().valueChanged.connect(self.SyncHorizontalScrollBar)
        self.shiftView.selectionModel().selectionChanged.connect(self.onSelectionChanged)
        self.shiftView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shiftView.setEditTriggers(QAbstractItemView.CurrentChanged)
        self.shiftView.setItemDelegate(ShiftDelegate())

        self.scrollView = BaseView()
        self.scrollView.hide()
        self.scrollView.setModel(self.shiftModel)
        self.scrollView.horizontalScrollBar().valueChanged.connect(self.SyncHorizontalScrollBar)
        self.scrollView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)
        self.scrollView.viewport().stackUnder(self.shiftView)

        self.countView = BaseView()
        self.countView.setModel(self.countModel)
        self.countView.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.countView.verticalScrollBar().valueChanged.connect(self.SyncVerticalScrollBar)

        self.nameView = BaseView()
        self.nameView.setModel(self.setHeaderName(data.yyyymm))
        self.nameView.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setColumnWidth()
        self.setRowHeight()
        self.setHeaderViewSize()

        layout = QGridLayout()
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.nameView, 0, 0)
        layout.addWidget(self.columnHeaderView, 0, 1)
        layout.addWidget(self.rowHeaderView, 1, 0)
        layout.addWidget(self.scrollView, 1, 1)
        layout.addWidget(self.shiftView, 1, 1)
        layout.addWidget(self.scrollView.horizontalScrollBar(), 2, 1)
        layout.addWidget(self.countView, 1, 2)
        layout.addWidget(self.scrollView.verticalScrollBar(), 1, 3)
        

        self.setLayout(layout)
        self.setContentsMargins(5, 0, 0, 0)
        self.setMinimumSize(1000, 400)

    def setHeaderName(self, date):
        date = date       
        name = pd.DataFrame(data=[[date[:7], '', '', '休日'],
                                  ['', '', '', ''],
                                  ['UID', 'ID', '氏名', '所属']])
        nameHeader = TableModel(name)
        
        return nameHeader

    def setColumnWidth(self):
        staffwidth = [30, 80, 100, 30]
        ncol = self.shiftModel.columnCount()
        for col in range(ncol):
            self.columnHeaderView.setColumnWidth(col, COLUMNWIDTH)
            self.shiftView.setColumnWidth(col, COLUMNWIDTH)
            self.scrollView.setColumnWidth(col, COLUMNWIDTH)
            if col < self.rowHeaderModel.columnCount():
                self.rowHeaderView.setColumnWidth(col, staffwidth[col])
                self.nameView.setColumnWidth(col, staffwidth[col])
            if col < self.countModel.columnCount():
                self.countView.setColumnWidth(col, COLUMNWIDTH)

    def setRowHeight(self):
        nrow = self.rowHeaderModel.rowCount()
        for row in range(nrow):
            self.rowHeaderView.setRowHeight(row, ROWHEIGHT)
            self.countView.setRowHeight(row, ROWHEIGHT)
            self.shiftView.setRowHeight(row, ROWHEIGHT)
            self.scrollView.setRowHeight(row, ROWHEIGHT)
            if row < self.columnHeaderModel.rowCount():
                self.columnHeaderView.setRowHeight(row, ROWHEIGHT)
                self.nameView.setRowHeight(row, ROWHEIGHT)


    
    def setHeaderViewSize(self):
        h = 0
        w = 0
        for row in range(self.columnHeaderModel.rowCount()):
            h += self.columnHeaderView.rowHeight(row)
        self.columnHeaderView.setFixedHeight(h)
        self.nameView.setFixedHeight(h)

        for col in range(self.rowHeaderModel.columnCount()):
            w += self.rowHeaderView.columnWidth(col)
        self.rowHeaderView.setFixedWidth(w)
        self.nameView.setFixedWidth(w)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        maxval = self.shiftView.horizontalScrollBar().maximum()
        self.scrollView.horizontalScrollBar().setMaximum(maxval)
        
        maxval = self.shiftView.verticalScrollBar().maximum()
        self.scrollView.verticalScrollBar().setMaximum(maxval)
        

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
        for ix in selected.indexes():
            # emphasize column,row header 
            for col in range(cols):
                index = self.rowHeaderView.model().index(ix.row(), col ,QModelIndex())
                self.rowHeaderView.model().setData(index, True, Qt.FontRole)
            for row in range(rows):
                index = self.columnHeaderView.model().index(row, ix.column(), QModelIndex())
                self.columnHeaderView.model().setData(index, True, Qt.FontRole)
        for ix in deselected.indexes():
            for col in range(cols):
                index = self.rowHeaderView.model().index(ix.row(), col ,QModelIndex())
                self.rowHeaderView.model().setData(index, False, Qt.FontRole)                
            for row in range(rows):
                index = self.columnHeaderView.model().index(row, ix.column(), QModelIndex())
                self.columnHeaderView.model().setData(index, False, Qt.FontRole)
                
class BaseView(QTableView):
    def __init__(self, parent=None, *args):
        super().__init__()
        
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)


class TableModel(QAbstractTableModel):
    def __init__(self, data, parent=None, *args):
        super().__init__()

        self._data = data

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
    def __init__(self, data, parent=None, *args):
        super().__init__(self, data, parent, *args)
        self._data = data
        self._font = [False for i in range(len(data))]
        self._color = [QColor('#00000000') for i in range(len(data))]

        self.setColor()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None
        value = self._data.iat[index.row(), index.column()]
        if role == Qt.DisplayRole:  
            return str(value)

        elif role == Qt.BackgroundRole:
            if index.column() == 3:
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
            dept = self._data.iat[row, 3]
            if dept in modalityColors:
                self._color[row] = modalityColors[dept]


class ColumnHeaderModel(TableModel):
    def __init__(self, data, closed, parent=None, *args):
        super().__init__(self, data, parent, *args)
        self._data = data
        self._closed = closed
        self.columnslist = data.columns.values
        self._font = [False for i in range(len(data.columns))]

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

    def setData(self, index, value, role):
        
        if index.isValid():
            if role == Qt.FontRole:
            
                self._font[index.column()] = value
                self.dataChanged.emit(index, index)
                return True
            else:
                return False
        else:
            return False


class ShiftModel(TableModel):
    def __init__(self, data, previous, request, parent=None, *args):
        super().__init__(self, data, parent, *args)
        self._data = data
        self._previous = previous
        self._request = request
        self.rowHeader = data.index.values #shiftのindexの値を配列にする
        
        self._color = pd.DataFrame(data=[[QColor('#00000000') for j in range(len(self._data.columns))] for i in range(len(self._data))])
        self._textColor = pd.DataFrame(data=[[QColor('#00000000') for j in range(len(self._data.columns))] for i in range(len(self._data))])
        self.setBackgroundColors()
        self.setTextColors()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None
        value = self._data.iat[index.row(), index.column()]
        previous = self._previous.iat[index.row(), index.column()]
        request = self._request.iat[index.row(), index.column()]

        if role == Qt.DisplayRole:
            if value == '勤':
                value = None
            if previous is not None:
                value = previous
            if request is not None:
                value = request
            return value

        elif role == Qt.BackgroundRole:
            return self._color.iat[index.row(), index.column()]   

        elif role == Qt.TextColorRole:
            return self._textColor.iat[index.row(), index.column()]

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter 
        return None  

    def setData(self, index, value, role=Qt.EditRole):
        previous = self._previous.iat[index.row(), index.column()]
        request = self._request.iat[index.row(), index.column()]        
        if previous is not None or request is not None:
            return False

        if role == Qt.EditRole:
            self._data.iat[index.row(), index.column()] = value
            self._color.iat[index.row(), index.column()] = shiftColors[value]
            self.dataChanged.emit(index, index)
            return True

        return False    

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


class ShiftDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ShiftDelegate, self).__init__(parent)
    
    def createEditor(self, parent, option, index):
        if index.model().previous_request(index):
            editor = QComboBox()
            editor.setParent(parent)
        
            # editor.setFrame(False)
            return editor
        else:
            return None

    def setEditorData(self, editor, index):
        shifts = ['休', '勤', 'A日', 'M日', 'C日', 'F日', 'A夜', 'M夜', 'C夜', '明']
        initval = index.model().data(index, Qt.DisplayRole)
        model = editor.model()       
        for item in shifts:
            stdItem = QStandardItem()
            stdItem.setBackground(shiftColors[item])    
            stdItem.setText(item)
            model.appendRow(stdItem)    
            # editor.addItem(stdItem)
        editor.setCurrentIndex(editor.findText(initval))

    def setModelData(self, editor, model, index):
        
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

class CountModel(TableModel):
    def __init__(self, data, parent=None, *args):
        super().__init__(data, parent, *args)
        self._data = data    

class AlphaModel(TableModel):
    def __init__(self, data, parent=None, *args):
        super().__init__(data, parent, *args)
        self._data = data
    
    def calcNum(self):
        return None


if __name__ == "__main__":

    app = QApplication(sys.argv)

    widget = ShiftTableWidget()
    widget.show()

    app.exec()