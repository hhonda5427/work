import logging
import sys
from PyQt5.QtWidgets import QApplication
from database.model4Kinmu import Model4Kinmu 

from util.shiftController import self, ShiftController
from view.mainWindow import MainWindow
from view.view import *
from controller.delegate import modelEditDelegate

app = QApplication(sys.argv)
shiftCtrl = ShiftController()
shiftChannel = self(shiftCtrl)
# print(shiftChannel.shiftCtrl.getKinmuForm(DataName.kinmu))

# delegate = modelEditDelegate()
Window = MainWindow(shiftChannel)
Window.show()

sys.exit(app.exec_())
