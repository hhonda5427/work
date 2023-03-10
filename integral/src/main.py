import logging
import sys
from PyQt5.QtWidgets import QApplication
from database.model4Kinmu import Model4Kinmu


from util.shiftController import ShiftChannel, ShiftController
from view.mainWindow import MainWindow
from view.view import *
from controller.delegate import modelEditDelegate

app = QApplication(sys.argv)
shiftCtrl = ShiftController()
shiftChannel = ShiftChannel(shiftCtrl)

Window = MainWindow(shiftChannel)
Window.show()

sys.exit(app.exec_())
