import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import shiftview, datamodel
import pyodbc

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)   
        data = datamodel.DataModel()
        self.rowHeaderModel = shiftview.RowHeaderModel(data.staffinfo)
        self.columnHeaderModel = shiftview.ColumnHeaderModel(data.header, data.closed)
        self.shiftModel = shiftview.ShiftModel(data.shiftdf, data.previousdf, data.requestdf)
        self.countModel = shiftview.CountModel(data.counttable)

        self.shiftView = shiftview.ShiftTableWidget(self.shiftModel, self.rowHeaderModel, self.columnHeaderModel, self.countModel)
        self.shiftView.setWindowTitle(data.yyyymm[:7] + '勤務表作成中')
        
        self.initUI()

        self.show()
        self.shiftView.show()


    def initUI(self):

        self.setWindowTitle('')
        self.setGeometry(50, 50, 400, 150)

        registerAction = QtWidgets.QAction('登録',self)
        registerAction.triggered.connect(self.register)
        exitAction = QtWidgets.QAction('終了', self)
        exitAction.triggered.connect(self.close)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('ファイル')
        fileMenu.addAction(registerAction)
        fileMenu.addAction(exitAction)

        btn1 = QtWidgets.QPushButton('夜勤表', self)   
        btn2 = QtWidgets.QPushButton('勤務表',self)
        
        btn1.clicked.connect(lambda:self.showTable(self.shiftView))

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(btn_layout)
        self.setCentralWidget(central_widget)

    def showTable(self, view):

        if view.isVisible():
            view.hide()
        else:
            view.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        
        self.shiftView.close()
        
        return super().closeEvent(a0)


    def register(self):
        '''
        ここに勤務表データベースへの登録用コードを書く
        '''
        print("register")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()
