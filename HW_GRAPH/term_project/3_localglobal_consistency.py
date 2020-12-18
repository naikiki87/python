import networkx as nx
import pandas as pd
from networkx.algorithms import node_classification
import sys

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 10000)

df = pd.DataFrame(columns = ['node', 'popularity'])

G = nx.Graph()

filename = "class_info.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
nodes = s.split('\n')

for i in range(len(nodes)) :
    data = nodes[i].split('\t')
    
    G.add_node(int(data[0]))
    if data[1] != '0' :
        G.nodes[i+1]['label'] = int(data[1])

file.close()

filename = "edge_list.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
edges = s.split('\n')

for i in range(len(edges)) :
    data = edges[i].split('\t')

    node_1 = data[0]
    node_2 = data[1]

    G.add_edge(node_1, node_2)

file.close()

lg_consis = node_classification.local_and_global_consistency(G)

for i in range(len(lg_consis)) :
    df.loc[len(df)] = [i+1, lg_consis[i]]

res = ''
for i in range(len(df)) :
    if i == (len(df)-1) :
        res = res + str(df.node[i]) + '\t' + str(df.popularity[i])
    else :
        res = res + str(df.node[i]) + '\t' + str(df.popularity[i]) + '\n'

filename = "res_local_global.txt"
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print(res)

sys.stdout = sys.__stdout__
f.close()