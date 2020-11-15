import matplotlib.pyplot as plt
from networkx import nx
import numpy as np
import collections
import math

region = 221

NODES = 10000
p = 0.8
K = 4

layout = nx.spring_layout

pvals = [0, 0.01, 0.1, 0.5]

for p in pvals :
    G = nx.watts_strogatz_graph(NODES, K, p=p)

    plt.subplot(region)
    region = region + 1
    plt.title("# Node : {}, p : {}".format(NODES, p))
    nx.draw_circular(G, node_color = "black", node_size = 1, width = 0.1, with_labels = False)             ## make circular model


plt.show()

# # degree distribution
# degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
# degreeCount = collections.Counter(degree_sequence)
# deg, cnt = zip(*degreeCount.items())

# plt.subplot(222)
# plt.title("Degree Distribution")
# plt.bar(deg, cnt, width=0.5, color="b")
# plt.xlabel('deg')
# plt.ylabel('count')


# # clusering coefficient
# plt.subplot(223)
# plt.title("Clustering Coefficient")

# x = []
# y = []
# p = 0
# for i in range(100) :
#     p = p + 0.01
#     G = return_watts(p)
#     CC = nx.average_clustering(G)
#     x.append(p)
#     y.append(CC)

# plt.plot(x, y, '.', markersize = 5, linewidth=0.1, color='b')

# ## CC theoretical
# x = []
# y = []
# p = 0

# CP_0 = (3*(K-2)) / (4*(K-1))

# for i in range(100) :
#     p = p + 0.01
#     C = CP_0 * math.pow(1-p, 3)

#     x.append(p)
#     y.append(C)

# plt.plot(x, y, '.', markersize = 3, linewidth=0.01, color='r')
# plt.xlabel('p')
# plt.ylabel('Clustering Coefficient')
# plt.xticks(np.arange(0, 1.1, 0.1))

# #diameter 구하기
# plt.subplot(224)
# plt.title("Diameter")

# x = []
# y = []
# p = 0
# for i in range(100) :
#     p = p + 0.01
#     G = return_watts(p)
#     dia = nx.diameter(G)
#     x.append(p)
#     y.append(dia)

# plt.plot(x, y, '.', markersize = 5, linewidth=0.1, color='b')
# plt.xlabel('p')
# plt.ylabel('Diameter')

# plt.show()