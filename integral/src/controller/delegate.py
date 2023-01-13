from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class modelEditDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(modelEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return QLineEdit(parent)

    def setEditorData(self, editor: QAbstractButton, index: QModelIndex):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor: QAbstractButton, model, index):
        model.setData(index, editor.text())
