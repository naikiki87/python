import networkx as nx
import numpy as np
import random as rd
import matplotlib.pyplot as plt
import warnings
import collections
import math

#### Create Watts-Strogatz network in different values of p
region = 221

NODES = 100
K = 4

layout = nx.spring_layout

pvals = [0, 0.01, 0.1, 0.5]

for p in pvals :
    G = nx.watts_strogatz_graph(NODES, K, p)

    plt.subplot(region)
    region = region + 1
    plt.title("# Node : {}, p : {}".format(NODES, p))
    nx.draw_circular(G, node_color = "black", node_size = 1, width = 0.1, with_labels = False)             ## make circular model

plt.show()


#### Analysis Intermediate steps

NODES = 410
VALUE_C = 4
region = 221
p = 0.5
K = 4

cnt_node = 4

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


G = nx.watts_strogatz_graph(NODES, K, p)

count = 0
new_node = cnt_node
for node in range(NODES - cnt_node):
    G.add_node(cnt_node + count)
    count += 1
    for e in range(0, VALUE_C):
        add_edge()
    new_node = new_node + 1

  ## show intermediate status
    if node % 100 == 0:
        if node == 0 :
            continue
        else :
            ### degree distribution
            # degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
            # degreeCount = collections.Counter(degree_sequence)
            # deg, cnt = zip(*degreeCount.items())
            # plt.subplot(region)
            # plt.bar(deg, cnt, width=0.5, color="b")
            # plt.plot(deg, cnt, '.-', markersize = 3, linewidth=1, color='r')
            # region = region + 1
            # plt.title("# Node : {}".format(node))
            # plt.ylabel("Count")
            # plt.xlabel("Degree")

            # ### clustering coefficient
            # cc = nx.average_clustering(G)
            # plt.bar(node, cc, width=0.5, color="b")

            # ## 이론값
            # c_0 = (3 * (node - 2)) / (4 * (node - 1))
            # cp = c_0 * math.pow(1-p, 3)
            # plt.plot(node, cp, '.-', markersize = 3, linewidth=1, color='r')

            # plt.title("p : {}".format(p))
            # plt.ylabel("Clustering Coefficient")
            # plt.xlabel("# node")
            # plt.xticks(np.arange(100, NODES, 100))

            ### diameter
            dia = nx.diameter(G)
            plt.bar(node, dia, width=1, color="b")

            plt.title("p : {}".format(p))
            plt.ylabel("diameter")
            plt.xlabel("# node")
            plt.xticks(np.arange(100, NODES, 100))

plt.show()