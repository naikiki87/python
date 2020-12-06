import networkx as nx
import config
################################################
# most_valuable_edge function:
# girvan-newman method는 edge의 value를 평가하여,
# 가장 중요한 edge부터 순차적으로 자르면서 community를 생성
# default는 edge-betweenness-centrality를 평가하는 것이며,
# 아래처럼 각자 함수를 정의하여 넘겨줄 수도 있음.
def most_valuable_edge_ebc(inputG):
    # edge betweenness centrality를 계산하여 가장 높은 edge를 리턴하는 함수
    ebc = nx.edge_betweenness_centrality(inputG)
    return max(ebc, key=ebc.get)

def most_valuable_edge_dispersion(inputG):
    # edge중에서 dispersion이 높은 edge를 리턴
    r_dict = {}
    for e in inputG.edges():
        u, v = e
        r_dict[e] = nx.dispersion(inputG, u, v)
    return max(r_dict.items(), key=lambda x: x[1])[0]
################################################

"""
girvan-newman method를 사용하여 community detection을 수행함. 
- most_valuable edge를 평가하는 방법을 변경하여 그 차이를 비교함.
1) edge betweenness centrality를 사용(default)
2) dispersion을 사용하여 edge의 중요도를 평가.
"""

# Generate graph
# N = 20
# G = nx.scale_free_graph(N, seed=0)
# G = nx.Graph(G)
G = config.G
assert nx.is_connected(G)==True
print("==" * 20)
print("== community detection by edge betweenness centrality")
community_generator = nx.algorithms.community.girvan_newman(
    G=G, most_valuable_edge=most_valuable_edge_ebc)  # type: generator

for i, communities_at_i in enumerate(community_generator):
    # n개의 node가 있을 때, n개의 community까지 분화할 수 있으므로,
    # n개로 분화되면 loop 탈출.
    print(f"== {i:2d} time.")
    for j, comm in enumerate(communities_at_i):
        print(f"community {j:2d} at time {i:2d} ==> {comm}")
    if i>=2:
        break
print("--" * 20)
print("--" * 20)
# community_generator = nx.algorithms.community.girvan_newman(
#     G=G, most_valuable_edge=most_valuable_edge_dispersion)  # type: generator
# for i, communities_at_i in enumerate(community_generator):
#     # n개의 node가 있을 때, n개의 community까지 분화할 수 있으므로,
#     # n개로 분화되면 loop 탈출.
#     print(f"== {i:2d} time.")
#     for j, comm in enumerate(communities_at_i):
#         print(f"community {j:2d} at time {i:2d} ==> {comm}")
#     if i >= 2:
#         break
# print("==" * 20)