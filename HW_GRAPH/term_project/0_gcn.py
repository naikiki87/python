import numpy as np

labels = []
nodes = []
X = []

filename = "class_info.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
nodes = s.split('\n')

for i in range(len(nodes)) :
    data = nodes[i].split('\t')
    nodes.append(data[0])
    labels.append(data[1])
    X.append(data[1:-1])

# print(X)

X = np.array(X,dtype=int)
N = X.shape[0] #the number of nodes
F = X.shape[1] #the size of node features
print('\nX shape: ', X.shape)
file.close()

filename = "edge_list.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
edges = s.split('\n')

edge_list=[]

for i in range(len(edges)) :
    data = edges[i].split('\t')
    edge_list.append((data[0], data[1]))

print('Number of nodes (N): ', N)
print('Number of features (F) of each node: ', F)
print('Categories: ', set(labels))

num_classes = len(set(labels))
print('Number of classes: ', num_classes)