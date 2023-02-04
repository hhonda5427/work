import logging
import sys, os
from PyQt5.QtWidgets import QApplication
from database.model4Kinmu import Model4Kinmu


from util.shiftController import ShiftChannel, ShiftController
from view.mainWindow import MainWindow
from view.view import *
from controller.delegate import modelEditDelegate
from settings import settings

# settings.readSettingJson()
# print(settings.ROOT_PATH)
# print(settings.DATABASE_PATH)
# print(os.getcwd().replace(os.sep, '/'))

app = QApplication(sys.argv)
shiftCtrl = ShiftController()
shiftChannel = ShiftChannel(shiftCtrl)


Window = MainWindow(shiftChannel)
Window.show()

sys.exit(app.exec_())
