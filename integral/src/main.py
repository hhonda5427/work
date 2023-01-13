import logging
import sys
from database.model4Kinmu import Model4Kinmu


from util.shiftController import ShiftChannel, ShiftController
from view.mainWindow import MainWindow
from view.view import *
from controller.delegate import modelEditDelegate

app = QtWidgets.QApplication(sys.argv)
shiftCtrl = ShiftController('PyQtPractice\data')
shiftChannel = ShiftChannel(shiftCtrl)
view = TestView()

delegate = modelEditDelegate()

testWindow = MainWindow(view, shiftChannel, delegate)
testWindow.show()

sys.exit(app.exec_())
