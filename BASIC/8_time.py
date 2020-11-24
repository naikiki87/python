import time
import datetime

# now = datetime.datetime.now()

# tm = time.gmtime(time.time())
# year = tm.tm_year
# t_hour = tm.tm_hour
# t_min = tm.tm_min
# t_sec = tm.tm_sec

# print("now : ", tm)
# print("year : ", year)

# WIN_SIZE = 10

# for i in range(WIN_SIZE-1, 0, -1) :
#     print(i)

temp = [None, None]
degree_list = []

temp = [time.time(), 16.5]
time.sleep(1)

cur_per = 19
if cur_per != temp[1] :
    cur_time = time.time()
    degree = (cur_per - temp[1]) / (time.time() - temp[0])

    degree_list.append(degree)

print("degree : ", degree_list)


a = [1,2,3,4]

b = list(map(str, a))

c = ','.join(b)

print("b : ", c)