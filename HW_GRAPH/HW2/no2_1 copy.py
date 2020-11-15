# coding: utf-8
import networkx as nx
import numpy as np
import random as rd
import matplotlib.pyplot as plt
import warnings

# https://github.com/AlxndrMlk/Barabasi-Albert_Network/blob/master/README.md
# 코드관련 README

init_nodes = 4 # 시작 노드의 수
final_nodes = 500 # 최종 노드의 수
m_parameter = 4 # 노드 생성 시 엣지 생성 수

G = nx.complete_graph(init_nodes) # 초기 complete_graph(4)

# 클러스터링 분석
def clustering_analysis(graph):
  for v in nx.nodes(G):
    print(f"{v} {nx.degree(G, v)} {nx.clustering(G, v)}")
  G_cluster = sorted(list(nx.clustering(graph).values()))
  print('average clustering coefficient: {}'.format(sum(G_cluster) / len(G_cluster)))

def rand_prob_node():
  nodes_probs = []
  for node in G.nodes():
    node_degr = G.degree(node)
    node_proba = node_degr / (2 * len(G.edges()))
    nodes_probs.append(node_proba)
  random_proba_node = np.random.choice(G.nodes(), p=nodes_probs)
  return random_proba_node


def add_edge():
  if len(G.edges()) == 0:
    random_proba_node = 0
  else:
    random_proba_node = rand_prob_node()
  new_edge = (random_proba_node, new_node)
  if new_edge in G.edges():
    add_edge()
  else:
    G.add_edge(new_node, random_proba_node)

count = 0
new_node = init_nodes
for f in range(final_nodes - init_nodes):
  if (f % 100  == 0):
    print("Step {} Success".format(count))

  G.add_node(init_nodes + count)
  count += 1
  for e in range(0, m_parameter):
    add_edge()
  new_node += 1

  # 생성된 노드가 100개마다 degree distribution 표현
  if (f % 100 == 0):
    """ Graph G의 degree 정보 """
    k = dict(nx.degree(G))
    """ histogram data 생성 """
    y, x = np.histogram(list(k.values()), bins=max(k.values()) - min(k.values()))
    x = x[:-1]
    y = y.astype('float')
    """ y축 normalizing """
    y /= np.sum(y)
    plt.plot(x, y, ls='', marker='.')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('k')
    plt.ylabel('P(k)')
    plt.show(block=False)
    clustering_analysis(G)

    print(nx.diameter(G))


print("\nFinal number of nodes ({}) reached".format(len(G.nodes())))

# clustering coefficient
clustering_analysis(G)

nx.draw(G)
plt.show()

# networkx의 지원 함수의 문제점: starting network 지정 문제
# G1 = nx.barabasi_albert_graph(n=100, m=4, seed=4