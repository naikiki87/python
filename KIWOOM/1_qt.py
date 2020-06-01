import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

app = QApplication(sys.argv)
label = QLabel("hello pyqt")
label.show()
app.exec_()