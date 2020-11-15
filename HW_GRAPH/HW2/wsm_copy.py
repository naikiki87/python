# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
from networkx import nx
import numpy as np
import collections

layout = nx.spring_layout

NODES = 100

def return_watts(a):
    ws = nx.watts_strogatz_graph(NODES, 4, p=a)
    return ws

# ws_0 = return_watts(0)
# ws_2 = return_watts(0.2)
# ws_4 = return_watts(0.4)
# ws_6 = return_watts(0.6)
# ws_8 = return_watts(0.8)
#print(nx.average_clustering(h))


# # degree distribution 구하기
# #첫번쨰 그래프 그리기
# degree_sequence = sorted([d for n, d in h.degree()], reverse=True)  # degree sequence
# degreeCount = collections.Counter(degree_sequence)
# deg, cnt = zip(*degreeCount.items())

# fig, ax = plt.subplots()
# plt.bar(deg, cnt, width=0.80, color="b")

# #두번째 그래프 그리기
# degree_sequence = sorted([d for n, d in h2.degree()], reverse=True)  # degree sequence
# print(degree_sequence)
# degreeCount = collections.Counter(degree_sequence)
# print(degreeCount)
# deg, cnt = zip(*degreeCount.items())
# plt.bar(deg, cnt, width=0.80, color="r")

# plt.title("Degree Histogram")
# plt.ylabel("Count")
# plt.xlabel("Degree")
# ax.set_xticks([d + 0.4 for d in deg])
# ax.set_xticklabels(deg)


#coefficient 구하기

# for i in range(2) :
#     print(nx.average_clustering(return_watts(0.1 * i)))


pvals = [0, 0.3, 0.6, 0.9]
region = 220  # for pylab 3x3 subplot layout
plt.subplots_adjust(left=0, right=1, bottom=0, top=0.95, wspace=0.1, hspace=0.1)
for p in pvals:
    G = return_watts(p)
    pos = layout(G)
    region += 1
    plt.subplot(region)
    plt.title(f"p = {p:.1f}")
    nx.draw_circular(G, node_color = "black", node_size = 1, width = 0.1, with_labels = False)             ## make circular model

# nx.draw_circular(ws_0, node_size = 1, width = 0.1, with_labels = False)             ## make circular model
# print(nx.diameter(h))
# print(nx.diameter(h2))
# print(nx.diameter(h3))
# #nx.draw(h)


plt.show()