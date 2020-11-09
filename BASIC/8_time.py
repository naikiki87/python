import time
import datetime

now = datetime.datetime.now()

tm = time.gmtime(time.time())
year = tm.tm_year
t_hour = tm.tm_hour
t_min = tm.tm_min
t_sec = tm.tm_sec

print("now : ", tm)
print("year : ", year)

WIN_SIZE = 10

for i in range(WIN_SIZE-1, 0, -1) :
    print(i)