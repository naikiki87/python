import collections
# from konlpy.tag import Hannanum
import networkx as nx
import matplotlib.pyplot as plt
import numpy.linalg
import sys
import io
import pandas as pd
import re

# pd.set_option('display.max_row', 20000)
# pd.set_option('display.max_columns', 10000)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

G = nx.Graph()
text_list = []

SUBJECT = "ADIDAS"
EXCEPT = ["the", "and", "a", "of", "for", "on", "in", "as", "by", "at", "was", "to", "but", "were", "that", "this", "its", "with", "which", "is", "an", "has", "had", "it", "from"]

filename = "testdata.txt"
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

            len_word = len(words[j])

            if words[j][len_word-1] == "은" or words[j][len_word-1] == "는" or words[j][len_word-1] == "이" or words[j][len_word-1] == "가":
                words[j] = words[j][0:len_word-1]

            if words[j] == "또" :
                continue

            words[j] = re.sub('[0-9]+', '', words[j])
            words[j] = re.sub('[A-Za-z]+', '', words[j])
            words[j] = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ·!』\\‘’|\(\)\[\]\<\>`\'…》]', '', words[j])

            # hannanum = Hannanum()
            # text_list = hannanum.nouns(words[j])

            text_list.append(words[j])

word_list = pd.Series(text_list)

print(word_list.value_counts())
#             G.add_node(words[j])
#             if cur != '' :
#                 G.add_edge(cur, words[j])
#                 cur = words[j]
#             else :
#                 cur = words[j]
# print(G.nodes())
# print(nx.info(G))
# print(nx.degree(G))


            # if '[' in words[j] :
            #     t = words[j].index('[')
            #     words[j] = words[j][0:t]

            # if ']' in words[j] :
            #     for k in range(len(words[j])) :
            #         if words[j][k] == '[' :
            #             words[j] = words[j][0:k]
            #             break
                    
            #         if k == (len(words[j]) - 1) :
            #             no_in = 1
                
            #     if no_in == 1 :
            #         no_in = 0
            #         continue

            # words[j] = words[j].lower()         # make lower character
            # words[j] = words[j].strip(',."?!:')         # 공백 제거

            # if words[j] in EXCEPT :
            #     continue
            # else :
            #     G.add_node(words[j])                # add node

            #     if cur != '' :
            #         G.add_edge(cur, words[j])
            #         cur = words[j]
            #     else :
            #         cur = words[j]

# nx.draw(G, with_labels = True)
# plt.show()