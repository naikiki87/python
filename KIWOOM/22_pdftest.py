import sys
import sqlite3
import time
import math
from time import localtime, strftime
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic, QtGui
import module_timer
import module_get_summary
import module_item_finder


df = pd.DataFrame(columns = ['time', 'type', 'T_ID', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])
print("1 : ", len(df))
print(df)
df.loc[0] = [1, 1, 1, 1, 1, 1, 1, 1]
df.loc[1] = [1, 1, 1, 1, 1, 1, 1, 1]
print("2 : ", len(df))
print(df)
df = df.drop(df.index[:len(df)])
print("3 : ", len(df))
print(df)