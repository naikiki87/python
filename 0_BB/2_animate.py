import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import random
import math
import numpy as np

pause = False

Gravity = 9.8

v0_km = random.randint(120, 140)
v0_m = v0_km * 1000 / 3600
angle = random.randint(35, 50)
print('v0_km : ', round(v0_m, 1), ", angle : ", angle)

radian = math.radians(angle)
sin = math.sin(radian)
cos = math.cos(radian)

t_max = (2 * v0_m * sin) / Gravity

def simData():
    dt = 0.1
    x = 0.0
    t = 0.0
    while t <= (t_max + 0.1):
        x = v0_m * cos * t
        y = v0_m * sin * t - 0.5 * Gravity * t * t
        t = t + dt
        
        if y >= 0 :
            yield x, y, t
        # if not pause:
        #     x = v0_m * cos * t
        #     y = v0_m * sin * t - 0.5 * Gravity * t * t
        #     t = t + dt
        # yield x, y, t

def onClick(event):
    global v0_m, angle, sin, cos, t_max

    v0_km = random.randint(120, 140)
    v0_m = v0_km * 1000 / 3600
    angle = random.randint(35, 50)
    radian = math.radians(angle)
    sin = math.sin(radian)
    cos = math.cos(radian)
    t_max = (2 * v0_m * sin) / Gravity

    print('v0_m : ', round(v0_m, 1), ", angle : ", angle)

    show_animation()
    # global pause
    # pause ^= True

def simPoints(simData):
    x, y, t = simData[0], simData[1], simData[2]
    time_text.set_text(time_template%(t))
    v0_text.set_text(v0_template%(v0_m))
    angle_text.set_text(angle_template%(angle))
    pos_x_text.set_text(pos_x_template%(x))
    pos_y_text.set_text(pos_y_template%(y))
    line.set_data(x, y)
    return line, time_text

fig = plt.figure()
ax = fig.add_subplot()
line, = ax.plot([], [], 'bo', ms=10)
ax.set_ylim(0, 50)
ax.set_xlim(-20, 130)

time_template = 'Time = %.1f s'
v0_template = 'v0 = %.1f m/s'
angle_template = 'Angle = %.1f º'
pos_x_template = 'X = %.1f m'
pos_y_template = 'Y = %.1f m'

v0_text = ax.text(0.1, 0.9, '', transform=ax.transAxes)
angle_text = ax.text(0.1, 0.85, '', transform=ax.transAxes)
time_text = ax.text(0.1, 0.8, '', transform=ax.transAxes)

pos_x_text = ax.text(0.5, 0.85, '', transform=ax.transAxes)
pos_y_text = ax.text(0.5, 0.8, '', transform=ax.transAxes)

fig.canvas.mpl_connect('button_press_event', onClick)

def show_animation() :
    ani = animation.FuncAnimation(fig, simPoints, simData, blit=False, interval=10, repeat=False)
    plt.show()

show_animation()