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

    def __init__(self, slot, delay_time):
        super().__init__()
        self.slot = slot
        self.delay_time = int(delay_time)

    def run(self):
        QtTest.QTest.qWait(self.delay_time)
        self.resume.emit(self.slot)