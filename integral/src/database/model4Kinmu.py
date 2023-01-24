
from PyQt5.QtCore import *
from pandas import DataFrame
from util.dataSender import DataName

from util.shiftController import ShiftChannel


class Model4Kinmu(QAbstractTableModel):

    changeTrigger = pyqtSignal(QModelIndex, str, str)

    def __init__(self, parent=None, shiftCtrlChannel: ShiftChannel = None):
        super().__init__(parent)
        self.kinmuDF = shiftCtrlChannel.shiftCtrl.getKinmuForm(DataName.kinmu)
        self.changeTrigger.connect(shiftCtrlChannel.updateMember)

    def data(self, index: QModelIndex, role: int):
        if role == Qt.ItemDataRole.EditRole or role == Qt.ItemDataRole.DisplayRole:
            return self.kinmuDF.iat[index.row(), index.column()]
        return QVariant()

    def rowCount(self, parent=QModelIndex()) -> int:
        return self.kinmuDF.shape[0]

    def columnCount(self, parent=QModelIndex()) -> int:
        return self.kinmuDF.shape[1]

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            self.changeTrigger.emit(index, value, self.__class__.__name__)

            print(
                f'データを編集しました。\n箇所: ({index.row()}, {index.column()})\n変更後: {value}')
            return True
        return False

    def updateDF(self, newDF: DataFrame):
        self.kinmuDF = newDF
