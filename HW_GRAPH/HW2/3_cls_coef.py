import networkx as nx
import collections
import matplotlib.pyplot as plt
import numpy as np

region = 221

print("clustering coefficient")
NODES = 10000
p = 0.8
K = 4

nvals = [10, 50, 100, 200]

for n in nvals :
# for i in range(4) :
    # n = n + 25
    x = []
    y = []
    p = 0
    for j in range(100) :
        p = p + 0.01
        # G = nx.erdos_renyi_graph(n, p)
        G = nx.watts_strogatz_graph(NODES, K, p=p)

        cls_coef = nx.average_clustering(G)
        x.append(p)
        y.append(cls_coef)

    plt.subplot(region)
    plt.plot(x, y, '.-', markersize = 1, linewidth=1, color='b')

    x = []
    y = []
    p = 0

    #### 이론값 -> C = p(빨간색)
    for i in range(100) :
        p = p + 0.01
        C = p

        x.append(p)
        y.append(C)

    plt.plot(x, y, '.', markersize = 2, linewidth=0.2, color='r')
    plt.title("# Node : {}".format(n))
    plt.xlabel('p')
    plt.ylabel('clustering coefficient')

    region = region + 1

plt.show()