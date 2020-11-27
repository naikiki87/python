# import os
# import time
# from datetime import datetime

# folder_dates = ['20190819', '20190820', '20190821']

# cnt = 0

# # for folder_date in folder_dates :
#     # folder_name = '../../gps_data/' + folder_date + '_after'
# folder_name = '../GPS_DATA'
# print("folder name : ", folder_name)
# for root, dirs, files in os.walk(folder_name):
#     for fname in files:
#         full_fname = os.path.join(root, fname)
#         file = open(full_fname, 'r', encoding='utf8')
#         s = file.read()
#         data = s.split('\n')
#         for i in range(len(data)) :
#             if i == 1 :
#                 break
#             logs = data[i].split(',')

#             date = logs[2]
#             year = date[0:4]
#             month = date[4:6]
#             day = date[6:8]

#             c_time = logs[3]
#             c_hour = c_time[0:2]
#             c_min = c_time[2:4]

#             for j in range(20) :
#                 ts = year + '-' + month + '-' + day + ' ' + c_hour + ':' + c_min + ':' + str(j*3)
#                 timestamp = time.mktime(datetime.strptime(ts, '%Y-%m-%d %H:%M:%S').timetuple())

#                 longitude = int(logs[5 + 3 * j]) / 360000;
#                 latitude = int(logs[6 + 3 * j]) / 360000;

#                 print(timestamp, longitude, latitude)

import random

for i in range(10) :
    print(i)
    i = i + 2
    # cnt = random.randint(1, 3)
    # print(cnt)