import matplotlib.pyplot as plt
import random
import math
import numpy as np

Gravity = 9.8

v0_km = random.randint(80, 130)
v0_m = v0_km * 1000 / 3600
angle = random.randint(1, 170)
print('v0_km : ', round(v0_m, 1), ", angle : ", angle)

radian = math.radians(angle)
sin = math.sin(radian)
cos = math.cos(radian)

t2 = (2 * v0_m * sin) / Gravity
times = np.arange(0, t2+0.1, 0.01)

ball_pos = []
xs = []
ys = []

for t in times :
    temp = []
    x = v0_m * cos * t                              
    y = v0_m * sin * t - 0.5 * Gravity * t * t

    if y < 0 :
        break
    else :
        xs.append(round(x, 1))
        ys.append(round(y, 1))
        # temp = [round(x, 1), round(y, 1)]
        # ball_pos.append(temp)

# print("xs : ", xs)
# print("ys : ", ys)

# plt.figure(figsize=(60, 100))
plt.xlim(-20, 150)
plt.ylim(0, 70)
plt.plot(xs, ys)
plt.show()