import networkx as nx
import collections
import matplotlib.pyplot as plt
import numpy as np
import operator as op
from functools import reduce
import math


## number of Connected Component
print("number of connected component")
n = 1
p = 0

region = 221
nvals = [10, 50, 100, 1000]

for n in nvals :
    x = []
    y = []
    p = 0

    for j in range(10) :
        p = p + 0.1
        G = nx.erdos_renyi_graph(n, p)

        cc = sorted(nx.connected_components(G), key=len, reverse=True)

        x.append(p)
        y.append(len(cc))
    
    plt.subplot(region)
    region = region + 1
    plt.plot(x, y, '.-', markersize=1, linewidth=1, color='r')
    plt.title("# Node : {}".format(n))
    plt.ylabel("# Conn Comp")
    plt.xlabel("p")
    plt.xticks(np.arange(0, 1.1, 0.1))

plt.show()

### Degree Distribution
print("degree distribution")
n = 1000
p = 0.6

x = []
y = []

def nCr(n, r) :
    r = min(r, n-r)
    numerator = reduce(op.mul, range(n, n-r, -1), 1)
    denominator = reduce(op.mul, range(1, r+1), 1)
    return numerator // denominator

k = np.arange(0, n, 1)
d = []

for i in range(len(k)) :
    dd2 = nCr(n-1, k[i]) * math.pow(p, k[i]) * math.pow(1-p, n-1-k[i])
    d.append(dd2)

plt.plot(k, d, '*-', markersize=2, linewidth=1, color='r')
plt.xlabel('k')
plt.ylabel('P(k)')
plt.xticks(np.arange(0, 1001, 100))

G = nx.erdos_renyi_graph(n, p)

degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
degreeCount = collections.Counter(degree_sequence)
deg, cnt = zip(*degreeCount.items())

temp_sum = 0

for i in range(len(cnt)) :
    temp_sum = temp_sum + cnt[i]
z = []
for i in range(len(cnt)) :
    z.append(round(cnt[i] / temp_sum, 2))

print("z : ", z)
plt.bar(deg, z, width=0.50, color="b")
plt.show()


### clustering coefficient
print("clustering coefficient")
region = 221

nvals = [10, 50, 100, 200]

for n in nvals :
# for i in range(4) :
    # n = n + 25
    x = []
    y = []
    p = 0
    for j in range(100) :
        p = p + 0.01
        G = nx.erdos_renyi_graph(n, p)

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


### Diameter
print("Diameter")
n = 100
x_val = np.arange(1, 11, 1)
p = 0.33

# for p in pvals :
for x in x_val :
    y = []
    G = nx.erdos_renyi_graph(n, p)
    path = dict(nx.shortest_path_length(G))
    max_val = 0

    for i in range(100) :
        for j in range(len(path[i])) :
            try :
                if path[i][j] > max_val :
                    max_val = path[i][j]
            except :
                pass
    print(p, "diameter : ", max_val)
    y.append(max_val)

    plt.bar(x, y, width=0.1, color="b")
plt.title("p : {}".format(p))
plt.xlabel('times')
plt.ylabel('diameter')
plt.xticks(np.arange(1, 11, 1))
plt.show()