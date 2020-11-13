import networkx as nx
import collections
import matplotlib.pyplot as plt

n = 10
p = 0.1

G = nx.erdos_renyi_graph(n, p)
# print(nx.connected_components(G))

Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
largest = max(nx.connected_components(G), key=len)

print("Gcc : ", Gcc)
print("Largest : ", largest)

S = [G.subgraph(c).copy() for c in nx.connected_components(G)]

print(S)
# print(nx.info(G))
# k = p * (n-1)
# print("k : ", k)

# for i in range(10) :
#     p = round((p + 0.001), 3)
#     k = p * (n-1)

#     print(p, ' : ', k)
# print("size : ", G.size())
# nx.draw(G, with_labels = True)
# plt.show()

# print("node degree clustering")
# for v in nx.nodes(G):
#     print(f"{v} {nx.degree(G, v)} {nx.clustering(G, v)}")

    
# print("diameter : ", nx.diameter(G))


# print("degree distribution")

# degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
# degreeCount = collections.Counter(degree_sequence)
# deg, cnt = zip(*degreeCount.items())

# fig, ax = plt.subplots()
# plt.bar(deg, cnt, width=0.80, color="b")

# plt.title("Degree Histogram")
# plt.ylabel("Count")
# plt.xlabel("Degree")
# ax.set_xticks([d + 0.4 for d in deg])
# ax.set_xticklabels(deg)
# plt.show()
