import datetime
import time

def whatday(day):
    return ['MON','TUE','WED','THU','FRI','SAT','SUN'][day]

c_time = time.localtime()
day = c_time.tm_wday

print(whatday(day))