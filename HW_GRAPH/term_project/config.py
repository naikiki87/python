import networkx as nx
import matplotlib.pyplot as plt

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