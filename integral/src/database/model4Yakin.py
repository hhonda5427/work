
from PyQt5.QtCore import *
from pandas import DataFrame

from util.shiftController import ShiftChannel


class Model4Yakin(QAbstractTableModel):

    def __init__(self, parent=None, shiftCtrlChannel: ShiftChannel = None):
        super().__init__(parent)
        self.yakinDF = shiftCtrlChannel.shiftCtrl.getYakinForm()

    def data(self, index: QModelIndex, role: int):
        if role == Qt.ItemDataRole.EditRole or role == Qt.ItemDataRole.DisplayRole:
            return self.yakinDF.iat[index.row(), index.column()]
        return QVariant()

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.yakinDF.shape[0]

    def columnCount(self, parent=QModelIndex()) -> int:
        return self.yakinDF.shape[1]

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            print(
                f'データを編集しました。\n箇所: ({index.row()}, {index.column()})\n変更後: {value}')

            return True
        return False

    def updateDF(self, newDF: DataFrame):
        self.yakinDF = newDF
