import sys
import time
import math
import datetime
import sqlite3
import config
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import requests
import threading
from bs4 import BeautifulSoup
import module_finder
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
class Delay(QThread):
    candidate = pyqtSignal(dict)
    resume = pyqtSignal(int)

    def run(self):
        QtTest.QTest.qWait(30000)
        self.resume.emit(1)