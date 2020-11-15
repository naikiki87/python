import networkx as nx
import collections
import matplotlib.pyplot as plt
import numpy as np
import math
import operator as op

from functools import reduce

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