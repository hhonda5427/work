
import logging
from Event.observer import Observer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database.model4Kinmu import Model4Kinmu
from database.model4Yakin import Model4Yakin
from Event.memberSubject import memberUpdateGenerator
from . import view
from util.shiftController import ShiftChannel




class MainWindow(QMainWindow):
    def __init__(self, shiftChannel: ShiftChannel):
        super().__init__()
        self.rowHeaderModel = view.RowHeaderModel(data.staffinfo)
        self.columnHeaderModel = view.ColumnHeaderModel(data.header, data.closed)
        self.shiftModel = view.ShiftModel(data.shiftdf, data.previousdf, data.requestdf)
        self.countModel = view.CountModel(data.counttable)

        self.memberElemObserver = MemberElemObserver(
            self.shiftModel, Model4Yakin(shiftCtrlChannel=shiftChannel))

        shiftChannel.addObserber(self.memberElemObserver)

        # self.view = view
        # self.delegate = delegate

        self.view.setModel(self.memberElemObserver.kinmuModel)  # とりあえず
        self.view.setItemDelegate(self.delegate)
        self.setCentralWidget(self.view)

        self.resize(1500, 800)

        self.shiftView = view.ShiftTableWidget(self.shiftModel, self.rowHeaderModel, self.columnHeaderModel, self.countModel)
        self.shiftView.setWindowTitle(shiftChannel.shiftCtrl.date + '勤務表作成中')
        
        self.initUI()

        self.show()
        self.shiftView.show()


    def initUI(self):

        self.setWindowTitle('')
        self.setGeometry(50, 50, 400, 150)

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
        
        btn1.clicked.connect(lambda:self.showTable(self.shiftView))

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

    def closeEvent(self, a0: QCloseEvent) -> None:
        
        self.shiftView.close()
        
        return super().closeEvent(a0)


    def register(self):
        '''
        ここに勤務表データベースへの登録用コードを書く
        '''
        print("register")



class MemberElemObserver(Observer):
    def __init__(self, kinmuModel: Model4Kinmu, yakinModel: Model4Yakin) -> None:
        super().__init__()
        self.kinmuModel = kinmuModel
        self.yakinModel = yakinModel

    def update(self, generator: memberUpdateGenerator):
        self.kinmuModel.updateDF(generator.getKinmuDF())
        self.yakinModel.updateDF(generator.getYakinDF())