import sys
from PyQt5.QtWidgets import QApplication


from util.shiftController import ShiftChannel, ShiftController
from view.mainWindow import MainWindow
from view.view import *

app = QApplication(sys.argv)
shiftCtrl = ShiftController()
shiftChannel = ShiftChannel(shiftCtrl)


Window = MainWindow(shiftChannel)
Window.show()

sys.exit(app.exec_())
