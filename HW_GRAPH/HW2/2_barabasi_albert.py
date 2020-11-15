import networkx as nx
import numpy as np
import random as rd
import matplotlib.pyplot as plt
import warnings
import collections

NODES = 510
VALUE_C = 4
region = 121

cnt_node = 4

G = nx.complete_graph(cnt_node)

def pref_attach():
  nodes_probs = []
  for node in G.nodes():
    node_degr = G.degree(node)
    node_proba = node_degr / (2 * len(G.edges()))
    nodes_probs.append(node_proba)
  dest_node = np.random.choice(G.nodes(), p=nodes_probs)
  return dest_node

def add_edge():
  if len(G.edges()) == 0:
    dest_node = 0
  else:
    dest_node = pref_attach()
  new_edge = (dest_node, new_node)
  if new_edge in G.edges():
    add_edge()
  else:
    G.add_edge(new_node, dest_node)

count = 0
new_node = cnt_node
for node in range(NODES - cnt_node):
  G.add_node(cnt_node + count)
  count += 1
  for e in range(0, VALUE_C):
    add_edge()
  new_node = new_node + 1

  ## show intermediate status
  if node % 250 == 0:
    if node == 0 :
      continue
    else :
      degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
      degreeCount = collections.Counter(degree_sequence)
      deg, cnt = zip(*degreeCount.items())

      temp_sum = 0

      for i in range(len(cnt)) :
          temp_sum = temp_sum + cnt[i]
      z = []
      for i in range(len(cnt)) :
          z.append(round(cnt[i] / temp_sum, 2))

      plt.subplot(region)
      # plt.bar(deg, cnt, width=0.5, color="b")
      # plt.plot(deg, cnt, '.-', markersize = 3, linewidth=1, color='r')
      region = region + 1
      plt.bar(deg, z, width=0.50, color="b")
      plt.plot(deg, z, '.-', markersize = 3, linewidth=1, color='b')

      x = []
      y = []
      for n, deg in G.degree() :
        print(n, "deg : ", deg)
        p_k = (2*VALUE_C * (VALUE_C + 1)) / (deg * (deg + 1) * (deg + 2))
        x.append(deg)
        y.append(p_k)
      
      plt.plot(x, y, '.-', markersize = 3, linewidth=1, color='r')

      # plt.subplot(region)
      # region = region + 1
      # plt.bar(deg, cnt, width=0.5, color="b")
      # plt.plot(deg, cnt, '.-', markersize = 3, linewidth=1, color='r')

      plt.title("# Node : {}".format(node))
      plt.ylabel("Count")
      plt.xlabel("Degree")
      plt.xscale('log')
      plt.yscale('log')


# clustering coefficient
print("Clustering Coefficient : ", nx.average_clustering(G))
print("Diameter : ", nx.diameter(G))
plt.show()