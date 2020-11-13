import networkx as nx
import matplotlib.pyplot as plt
import math
import pandas as pd
import sys

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 100)

G = nx.DiGraph()

# SUBJECT = "ADIDAS"
SUBJECT = "NIKE"
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
            words[j] = words[j].strip(',."?!:')         # 

            if words[j] in EXCEPT :
                continue
            else :
                G.add_node(words[j])                # add node

                if cur != '' :
                    G.add_edge(cur, words[j])
                    cur = words[j]
                else :
                    cur = words[j]

nx.draw(G, with_labels = True)
plt.show()

print("info : ", nx.info(G))

############ eigenvector centrality ############
print("eigenvector centrality")

df_eigv_centrality = pd.DataFrame(columns = ['word', 'eigv_centrality'])

for key, value in nx.eigenvector_centrality(G).items() :
    df_eigv_centrality.loc[len(df_eigv_centrality)] = [key, value]

df_eigv_centrality = df_eigv_centrality.sort_values(by=['eigv_centrality'], axis=0, ascending=False)
df_eigv_centrality = df_eigv_centrality.reset_index(drop=True, inplace=False)

filename = './result/' + SUBJECT + '/directed/eigv_centrality.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "eigv_centrality")
print(df_eigv_centrality)

sys.stdout = sys.__stdout__
f.close()


########## katz #################
print("katz")
df_katz_centrality = pd.DataFrame(columns = ['word', 'katz_centrality'])

katz = nx.katz_centrality(G, alpha=0.1, beta=1.0, max_iter=100000, tol=1.0e-6, nstart=None, normalized=True, weight = 'weight')
for key, value in katz.items() :
    df_katz_centrality.loc[len(df_katz_centrality)] = [key, value]

df_katz_centrality = df_katz_centrality.sort_values(by=['katz_centrality'], axis=0, ascending=False)
df_katz_centrality = df_katz_centrality.reset_index(drop=True, inplace=False)

filename = './result/' + SUBJECT + '/directed/katz_centrality.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "katz_centrality")
print(df_katz_centrality)

sys.stdout = sys.__stdout__
f.close()


# ########### pagerank ############
print("pagerank")

df_pagerank = pd.DataFrame(columns = ['word', 'pagerank'])

for key, value in nx.pagerank(G).items() :
    df_pagerank.loc[len(df_pagerank)] = [key, value]

df_pagerank = df_pagerank.sort_values(by=['pagerank'], axis=0, ascending=False)
df_pagerank = df_pagerank.reset_index(drop=True, inplace=False)

filename = './result/' + SUBJECT + '/directed/pagerank.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "PageRank")
print(df_pagerank)

sys.stdout = sys.__stdout__
f.close()


########### closeness centrality ############
print("closeness centrality")

df_closeness_centrality = pd.DataFrame(columns = ['word', 'closeness_centrality'])

for key, value in nx.closeness_centrality(G).items() :
    df_closeness_centrality.loc[len(df_closeness_centrality)] = [key, value]

df_closeness_centrality = df_closeness_centrality.sort_values(by=['closeness_centrality'], axis=0, ascending=False)
df_closeness_centrality = df_closeness_centrality.reset_index(drop=True, inplace=False)

filename = './result/' + SUBJECT + '/directed/closeness_centrality.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "closeness_centrality")
print(df_closeness_centrality)

sys.stdout = sys.__stdout__
f.close()


########### betweenness centrality ############
print("betweenness centrality")

df_btw_centrality = pd.DataFrame(columns = ['word', 'btw_centrality'])

for key, value in nx.betweenness_centrality(G).items() :
    df_btw_centrality.loc[len(df_btw_centrality)] = [key, value]

df_btw_centrality = df_btw_centrality.sort_values(by=['btw_centrality'], axis=0, ascending=False)
df_btw_centrality = df_btw_centrality.reset_index(drop=True, inplace=False)

filename = './result/' + SUBJECT + '/directed/betweenness_centrality.txt'
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print("SUBJECT : ", SUBJECT)
print("Title : ", "btw_centrality")
print(df_btw_centrality)

sys.stdout = sys.__stdout__
f.close()