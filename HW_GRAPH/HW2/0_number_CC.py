import networkx as nx
import collections
import matplotlib.pyplot as plt
import numpy as np

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




# x = []
# y = []

# #### p가 0.1 단위로 커질때
# for i in range(10) :
#     p = p + 0.1
#     G = nx.erdos_renyi_graph(n, p)

#     cc = sorted(nx.connected_components(G), key=len, reverse=True)

#     # print("p : ", round(p, 2), "/ Count : ", len(cc))
#     # print("cc : ", cc)

#     x.append(p)
#     y.append(len(cc))

# plt.plot(x, y, '.-', markersize = 1, linewidth=1)


# x = []
# y = []
# p = 0

# #### p가 0.01 단위로 커질때
# for i in range(100) :
#     p = p + 0.01
#     G = nx.erdos_renyi_graph(n, p)

#     cc = sorted(nx.connected_components(G), key=len, reverse=True)

#     # print("p : ", round(p, 2), "/ Count : ", len(cc))
#     # print("cc : ", cc)

#     x.append(p)
#     y.append(len(cc))




# plt.plot(x, y, '.-', markersize=1, linewidth=1, color='r')


# x = []
# y = []
# p = 0

# #### p가 0.01 단위로 커질때
# for i in range(1000) :
#     p = p + 0.001
#     G = nx.erdos_renyi_graph(n, p)

#     cc = sorted(nx.connected_components(G), key=len, reverse=True)

#     x.append(p)
#     y.append(len(cc))


# plt.plot(x, y, '.-', markersize=1, linewidth=1, color='r')

# plt.xlabel('probablity')
# plt.ylabel('# of Connected Component')
# plt.xticks(np.arange(0, 1.1, 0.1))
# plt.show()