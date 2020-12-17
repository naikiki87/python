import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

G = nx.Graph()
label_list = []

filename = "class_info.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
nodes = s.split('\n')

for i in range(len(nodes)) :
    data = nodes[i].split('\t')

    G.add_node(data[0], label=data[1])
    label_list.append(data[1])


    # G.add_node(data[0])                # add node
    # G.nodes[i]["label"] = data[1]
    # G.nodes[data[0]]['label'] = data[1]

file.close()

# print(G.nodes(data=True))
# print(label_list)

filename = "edge_list.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
edges = s.split('\n')

for i in range(len(edges)) :
    data = edges[i].split('\t')

    node_1 = data[0]
    node_2 = data[1]

    G.add_edge(node_1, node_2)

# print("info : ", nx.info(G))

# nx.draw(G, with_labels = True)
# plt.show()

print("degree centrality")

deg_centrality = pd.DataFrame(columns = ['word', 'deg_centrality'])

for key, value in nx.degree_centrality(G).items() :
    deg_centrality.loc[len(deg_centrality)] = [key, value]

deg_centrality = deg_centrality.sort_values(by=['deg_centrality'], axis=0, ascending=False)
deg_centrality = deg_centrality.reset_index(drop=True, inplace=False)

print(deg_centrality)

print("eigenvector centrality")

df_eigv_centrality = pd.DataFrame(columns = ['word', 'eigv_centrality'])

for key, value in nx.eigenvector_centrality(G).items() :
    df_eigv_centrality.loc[len(df_eigv_centrality)] = [key, value]

df_eigv_centrality = df_eigv_centrality.sort_values(by=['eigv_centrality'], axis=0, ascending=False)
df_eigv_centrality = df_eigv_centrality.reset_index(drop=True, inplace=False)

print(df_eigv_centrality)


# ########### pagerank ############
print("pagerank")

df_pagerank = pd.DataFrame(columns = ['word', 'pagerank'])

for key, value in nx.pagerank(G).items() :
    df_pagerank.loc[len(df_pagerank)] = [key, value]

df_pagerank = df_pagerank.sort_values(by=['pagerank'], axis=0, ascending=False)
df_pagerank = df_pagerank.reset_index(drop=True, inplace=False)

print(df_pagerank)


########### closeness centrality ############
print("closeness centrality")

df_closeness_centrality = pd.DataFrame(columns = ['word', 'closeness_centrality'])

for key, value in nx.closeness_centrality(G).items() :
    df_closeness_centrality.loc[len(df_closeness_centrality)] = [key, value]

df_closeness_centrality = df_closeness_centrality.sort_values(by=['closeness_centrality'], axis=0, ascending=False)
df_closeness_centrality = df_closeness_centrality.reset_index(drop=True, inplace=False)

print(df_closeness_centrality)


########### betweenness centrality ############
print("betweenness centrality")

df_btw_centrality = pd.DataFrame(columns = ['word', 'btw_centrality'])

for key, value in nx.betweenness_centrality(G).items() :
    df_btw_centrality.loc[len(df_btw_centrality)] = [key, value]

df_btw_centrality = df_btw_centrality.sort_values(by=['btw_centrality'], axis=0, ascending=False)
df_btw_centrality = df_btw_centrality.reset_index(drop=True, inplace=False)
print(df_btw_centrality)