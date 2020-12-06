import collections
import networkx as nx
import matplotlib.pyplot as plt
import numpy.linalg
import sys
import io
import pandas as pd

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 10000)

G = nx.Graph()

# SUBJECT = "NIKE"
SUBJECT = "ADIDAS"
EXCEPT = ["the", "and", "a", "of", "for", "on", "in", "as", "by", "at", "was", "to", "but", "were", "that", "this", "its", "with", "which", "is", "an", "has", "had", "it", "from"]

filename = SUBJECT + ".txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
data = s.split('\n')

pre = ''
cur = ''
no_in = 0

for i in range(len(data)) :
    words = data[i].split(' ')
    if words[0] == '' :
        a = 1
    else :
        for j in range(len(words)) :
            words[j] = words[j].strip()         # 공백 제거

            if '[' in words[j] :
                t = words[j].index('[')
                words[j] = words[j][0:t]

            if ']' in words[j] :
                for k in range(len(words[j])) :
                    if words[j][k] == '[' :
                        words[j] = words[j][0:k]
                        break
                    
                    if k == (len(words[j]) - 1) :
                        no_in = 1
                
                if no_in == 1 :
                    no_in = 0
                    continue

            words[j] = words[j].lower()         # make lower character
            words[j] = words[j].strip(',."?!:')         # 공백 제거

            if words[j] in EXCEPT :
                continue
            else :
                G.add_node(words[j])                # add node

                if cur != '' :
                    G.add_edge(cur, words[j])
                    cur = words[j]
                else :
                    cur = words[j]

# nx.draw(G, with_labels = True)
# plt.show()


print("basic information")
# filename = SUBJECT + "_basicinfo.txt"
filename = './result/' + SUBJECT + '/undirected/basic_info.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "Basic Infomation")
print(nx.info(G))
print("Density : ", nx.density(G))

df_info = pd.DataFrame(columns = ['word', 'degree'])

temp = dict(nx.degree(G))

for key, value in temp.items() :
    df_info.loc[len(df_info)] = [key, value]

df_info = df_info.sort_values(by=['degree'], axis=0, ascending=False)
df_info = df_info.reset_index(drop=True, inplace=False)

print(df_info)

sys.stdout = sys.__stdout__
f.close()


#################### degree distribution ###################
print("degree distribution")

degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
degreeCount = collections.Counter(degree_sequence)
deg, cnt = zip(*degreeCount.items())

fig, ax = plt.subplots()
plt.bar(deg, cnt, width=0.80, color="b")

plt.title("Degree Histogram")
plt.ylabel("Count")
plt.xlabel("Degree")
ax.set_xticks([d + 0.4 for d in deg])
ax.set_xticklabels(deg)
plt.show()


####################### Laplacian ########################
print("graph laplacian")
filename = './result/' + SUBJECT + '/undirected/laplacian.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "Graph Laplacian")
temp = nx.laplacian_matrix(G, nodelist=None, weight='weight')
df = pd.DataFrame(temp.toarray())
print(df)

sys.stdout = sys.__stdout__
f.close()

####################### eigenvalues ####################
print("eigenvalues")

L = nx.normalized_laplacian_matrix(G)
e = numpy.linalg.eigvals(L.A)

plt.hist(e, bins=100)  # histogram with 100 bins
plt.xlim(-0.5, 2.5)  # eigenvalues between -0.5 and 2.5
plt.title("Eigenvalues")
plt.ylabel("Count")
plt.xlabel("eigenvalues")
plt.show()

filename = './result/' + SUBJECT + '/undirected/eigenvalues.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "eigenvalues")
print("- Largest eigenvalue:", max(e))
print("- Smallest eigenvalue:", min(e))
# print("- Second Smallest eigenvalue:", nsmallest(2, e)[-1])

e.sort()
print("- second smallest : ", e[1])

print("- eigenvalues -")
for i in range(len(e)) :
    print(e[i])

sys.stdout = sys.__stdout__
f.close()


##################### clustering #####################
print("clustering coefficient")
df_cls = pd.DataFrame(columns = ['word', 'cls'])

for key, value in nx.clustering(G).items() :
    df_cls.loc[len(df_cls)] = [key, value]

df_cls = df_cls.sort_values(by=['cls'], axis=0, ascending=False)
df_cls = df_cls.reset_index(drop=True, inplace=False)

filename = './result/' + SUBJECT + '/undirected/clustering_coefficient.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "Clustering Coefficient")
print("Average : ", nx.average_clustering(G))
print(df_cls)

f.close()