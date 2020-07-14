# import time

# now = time.localtime()

# c_hour = now.tm_hour
# c_min = now.tm_min
# c_sec = now.tm_sec


# print(c_hour, c_min.toString(), c_sec)

# now_str = str(c_hour) + ':' + str(c_min) + ':' +  str(c_sec)
# a = int(str(c_hour) + str(c_min) + str(c_sec))

# print(now_str)
# print(a)


import datetime

now = datetime.datetime.now()
today8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
mkt_open = now.replace(hour=9, minute=0, second=0)
mkt_close = now.replace(hour=15, minute=20, second=0)

c_hour = now.strftime('%H')
c_min = now.strftime('%M')
c_sec = now.strftime('%S')

str_time = c_hour + ':' + c_min + ':' + c_sec

print("A : ", str_time)

if now >= mkt_open and now < mkt_close :
    print("can")
else :
    print("can't")