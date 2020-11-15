import networkx as nx
import collections
import matplotlib.pyplot as plt
import numpy as np

# nvals = [100, 10]
# region = 121

# for n in nvals :
#     x = []
#     y = []
#     p = 0

#     for i in range(10) :
#         p = p + 0.1
#         G = nx.erdos_renyi_graph(n, p)

#         x.append(p)

#         try :
#             diameter = nx.diameter(G)
#             y.append(diameter)

#         except :
#             y.append(0)

#     plt.subplot(region)
#     plt.bar(x, y, '.-', markersize = 2, linewidth=1, color='b')
#     # plt.bar(x, y, width=0.05, color="b")
#     plt.xlabel('p')
#     plt.ylabel('diameter')
#     plt.title("# Node : {}".format(n))

#     plt.xticks(np.arange(0, 1.1, 0.1))
#     region = region + 1
# plt.show()

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