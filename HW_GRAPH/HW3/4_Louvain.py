import community as community_louvain
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import config
import time

start = time.time()

G = config.G

# compute the best partition
partition = community_louvain.best_partition(G)

temp = []
dictlist = []

for key, value in partition.items():
    temp = [key,value]
    dictlist.append(temp)

val_cluster = []

for i in range(len(dictlist)) :
    cluster = dictlist[i][1]

    if cluster not in val_cluster :
        val_cluster.append(cluster)

for cluster in val_cluster :
    group = []
    for i in range(len(dictlist)) :
        if dictlist[i][1] == cluster :
            group.append(dictlist[i][0])
    
    print(cluster, ' : ', group)

print("time : ", time.time() - start)

## draw the graph
# pos = nx.spring_layout(G)
# cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
# nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=40,
#                        cmap=cmap, node_color=list(partition.values()))
# nx.draw_networkx_edges(G, pos, alpha=0.5)
# plt.show()