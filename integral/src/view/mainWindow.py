
# import logging
# from Event.observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from database.model4Kinmu import Model4Kinmu
# from database.model4Yakin import Model4Yakin
# from Event.memberSubject import memberUpdateGenerator
# from util.dataSender import DataSender, DataName
from . import view, yakinview
from util.shiftController import ShiftChannel
from view.datamodel import *

class MainWindow(QMainWindow):
    def __init__(self, shiftChannel: ShiftChannel):
        super().__init__()
        
        self.shiftChannel = shiftChannel
        self.rowHeaderModel = view.RowHeaderModel(shiftChannel)
        self.columnHeaderModel = view.ColumnHeaderModel(shiftChannel)
        self.shiftModel = view.ShiftModel(shiftChannel)
        self.countModel = view.CountModel(shiftChannel)
        
        self.yakinModel = yakinview.Model(shiftChannel)

        self.shiftModel.dataChanged.connect(self.refreshYakinTable)
        self.yakinModel.dataChanged.connect(self.refreshKinmuTable)
        


        self.resize(1500, 800)

        self.shiftView = view.ShiftTableWidget( self.shiftModel,
                                                self.rowHeaderModel,
                                                self.columnHeaderModel,
                                                self.countModel)
        
        self.yakinView = yakinview.nightshiftDialog(self.yakinModel, shiftChannel)
        
        # selectionModel = self.yakinView.view.selectionModel()
        # selectionModel.selectionChanged.connect(self.refreshYakinAppearance)


        self.initUI()

        self.show()
        self.shiftView.show()
        self.yakinView.show()

    

    def initUI(self):

        self.setWindowTitle('メイン')
        self.shiftView.setWindowTitle('勤務表')
        self.yakinView.setWindowTitle('夜勤表')
        self.setGeometry(50, 50, 400, 100)

        registerAction = QAction('登録',self)
        registerAction.triggered.connect(self.register)
        exitAction = QAction('終了', self)
        exitAction.triggered.connect(self.close)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('ファイル')
        fileMenu.addAction(registerAction)
        fileMenu.addAction(exitAction)

        btn1 = QPushButton('夜勤表', self)   
        btn2 = QPushButton('勤務表',self)
        
        btn1.clicked.connect(lambda:self.showTable(self.yakinView))
        btn2.clicked.connect(lambda:self.showTable(self.shiftView))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn1)
        btn_layout.addWidget(btn2)

        central_widget = QWidget()
        central_widget.setLayout(btn_layout)
        self.setCentralWidget(central_widget)

    def showTable(self, view):

        if view.isVisible():
            view.hide()
        else:
            view.show()
      
    def refreshYakinTable(self):
        self.yakinModel.refreshData()
        self.yakinView.view.viewport().update()

    # def refreshYakinAppearance(self, selected, deselected):
    #     self.yakinModel.update_cell_color(selected, deselected)
    #     self.yakinView.view.viewport().update()

    def refreshKinmuTable(self):
        self.shiftModel.refreshData()
        self.shiftView.shiftView.viewport().update()

    def closeEvent(self, a0: QCloseEvent) -> None:
        
        self.shiftView.close()
        self.yakinView.candidate.close()
        self.yakinView.close()
        return super().closeEvent(a0)


    def register(self):
        '''
        ここに勤務表データベースへの登録用コードを書く
        '''
        print("register")
        ret = QMessageBox.information(None, "登録確認", "勤務表をデータベースに登録しますか", 
                                     QMessageBox.Yes, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.shiftChannel.shiftCtrl.send2accdb()
        elif ret == QMessageBox.No:
            pass


# class MemberElemObserver(Observer):
#     def __init__(self, kinmuModel: Model4Kinmu, yakinModel: Model4Yakin) -> None:
#         super().__init__()
#         self.kinmuModel = kinmuModel
#         self.yakinModel = yakinModel

#     def update(self, generator: memberUpdateGenerator):
#         self.kinmuModel.updateDF(generator.getKinmuDF())
#         self.yakinModel.updateDF(generator.getYakinDF())
