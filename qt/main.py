import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import shiftview, datamodel

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        data = datamodel.DataModel()
        self.rowHeaderModel = shiftview.RowHeaderModel(data.staffinfo)
        self.columnHeaderModel = shiftview.ColumnHeaderModel(data.header, data.closed)
        self.shiftModel = shiftview.ShiftModel(data.shiftdf, data.previousdf, data.requestdf)
        self.countModel = shiftview.CountModel(data.counttable)

        self.shiftView = shiftview.ShiftTableWidget(self.shiftModel, self.rowHeaderModel, self.columnHeaderModel, self.countModel, data)
        
        
        
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.shiftView)
        self.setCentralWidget(QtWidgets.QWidget())
        central_widget = self.centralWidget()
        central_widget.setLayout(layout)
        
        self.show()
        


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
