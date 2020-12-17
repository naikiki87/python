import networkx as nx
import config
from networkx.algorithms import node_classification
import pandas as pd
import sys

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 10000)

from networkx.utils.decorators import not_implemented_for
from networkx.algorithms.node_classification.utils import (
    _get_label_info,
    _init_label_matrix,
    _propagate,
    _predict,
)


G = nx.Graph()
label_list = []

filename = "class_info.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
nodes = s.split('\n')

df_graph = pd.DataFrame(columns = ['web_site', 'popularity'])

for i in range(len(nodes)) :
    data = nodes[i].split('\t')
    df_graph.loc[len(df_graph)] = [data[0], int(data[1])]

file.close()

# print(df_graph)

G = config.G

df_info = pd.DataFrame(columns = ['web_site', 'degree', 'pop'])

temp = dict(nx.degree(G))

for key, value in temp.items() :
    df_info.loc[len(df_info)] = [key, value, 10]

df_info = df_info.sort_values(by=['degree'], axis=0, ascending=False)
df_info = df_info.reset_index(drop=True, inplace=False)

# print(df_info)

for i in range(len(df_info)) :
    target = df_info.web_site[i]

    for j in range(len(df_graph)) :
        if df_graph.web_site[j] == target :
            df_info.loc[i] = [df_info.web_site[i], df_info.degree[i], df_graph.popularity[j]]
            break

print(df_info)




# df_pagerank = pd.DataFrame(columns = ['web_site', 'pagerank', 'pop'])

# for key, value in nx.pagerank(G).items() :
#     df_pagerank.loc[len(df_pagerank)] = [key, value, 10]

# df_pagerank = df_pagerank.sort_values(by=['pagerank'], axis=0, ascending=False)
# df_pagerank = df_pagerank.reset_index(drop=True, inplace=False)

# # print(df_pagerank)

# for i in range(len(df_pagerank)) :
#     target = df_pagerank.web_site[i]

#     for j in range(len(df_graph)) :
#         if df_graph.web_site[j] == target :
#             df_pagerank.loc[i] = [df_pagerank.web_site[i], df_pagerank.pagerank[i], df_graph.popularity[j]]
#             break

# print(df_pagerank)

# filename = "res_pagerank.txt"
# f = open(filename,'w', encoding='utf8')
# sys.stdout = f
# print("Title : ", "PageRank")
# print(df_pagerank)

# sys.stdout = sys.__stdout__
# f.close()

