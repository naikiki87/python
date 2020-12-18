import networkx as nx
import pandas as pd
import random
import numpy as np
import sys
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 10000)

## 1. 그래프 생성
G = nx.Graph()
df_graph = pd.DataFrame(columns=['node', 'popularity', 'C_deg', 'pagerank', 'C_btw', 'C_eigen', 'C_close'])

filename = "class_info.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
nodes = s.split('\n')
label = []

for i in range(len(nodes)) :
    data = nodes[i].split('\t')
    df_graph.loc[len(df_graph)] = [int(data[0]), int(data[1]), 0, 0, 0, 0, 0]
    G.add_node(data[0])
    label.append(data[1])
        
file.close()

filename = "edge_list.txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
edges = s.split('\n')

for i in range(len(edges)) :
    data = edges[i].split('\t')
    G.add_edge(data[0], data[1])

file.close()



## 2. 그래프 특성 생성
print("2-1 Add degree centrality")
deg_centrality = pd.DataFrame(columns = ['node', 'deg_centrality'])

for key, value in nx.degree_centrality(G).items() :
    deg_centrality.loc[len(deg_centrality)] = [key, value]

for i in range(len(df_graph)) :
    target = df_graph.node[i]
    
    for j in range(len(deg_centrality)) :
        if int(deg_centrality.node[j]) == target :
            df_graph.loc[i] = [df_graph.node[i], df_graph.popularity[i], int(deg_centrality.deg_centrality[j] * 1000000), df_graph.pagerank[i], df_graph.C_btw[i], df_graph.C_eigen[i], df_graph.C_close[i]]

print("2-2 Add pagerank")
df_pagerank = pd.DataFrame(columns = ['node', 'pagerank'])
for key, value in nx.pagerank(G).items() :
    df_pagerank.loc[len(df_pagerank)] = [key, value]

for i in range(len(df_graph)) :
    target = df_graph.node[i]
    for j in range(len(df_pagerank)) :
        if int(df_pagerank.node[j]) == target :
            df_graph.loc[i] = [df_graph.node[i], df_graph.popularity[i], df_graph.C_deg[i], int(df_pagerank.pagerank[j] * 1000000), df_graph.C_btw[i], df_graph.C_eigen[i], df_graph.C_close[i]]

print("2-3 Add betweenness centrality")
df_btw_centrality = pd.DataFrame(columns = ['node', 'btw_centrality'])

for key, value in nx.betweenness_centrality(G).items() :
    df_btw_centrality.loc[len(df_btw_centrality)] = [key, value]

for i in range(len(df_graph)) :
    target = df_graph.node[i]
    for j in range(len(df_btw_centrality)) :
        if int(df_btw_centrality.node[j]) == target :
            df_graph.loc[i] = [df_graph.node[i], df_graph.popularity[i], df_graph.C_deg[i], df_graph.pagerank[i], int(df_btw_centrality.btw_centrality[j] * 1000000), df_graph.C_eigen[i], df_graph.C_close[i]]

print("2-4 Add eigenvector centrality")
df_eigv_centrality = pd.DataFrame(columns = ['node', 'eigv_centrality'])

for key, value in nx.eigenvector_centrality(G).items() :
    df_eigv_centrality.loc[len(df_eigv_centrality)] = [key, value]

for i in range(len(df_graph)) :
    target = df_graph.node[i]
    for j in range(len(df_eigv_centrality)) :
        if int(df_eigv_centrality.node[j]) == target :
            df_graph.loc[i] = [df_graph.node[i], df_graph.popularity[i], df_graph.C_deg[i], df_graph.pagerank[i], df_graph.C_btw[i], int(df_eigv_centrality.eigv_centrality[j] * 1000000), df_graph.C_close[i]]

print("2-5 Add closeness centrality")
df_closeness_centrality = pd.DataFrame(columns = ['node', 'closeness_centrality'])

for key, value in nx.closeness_centrality(G).items() :
    df_closeness_centrality.loc[len(df_closeness_centrality)] = [key, value]

for i in range(len(df_graph)) :
    target = df_graph.node[i]
    for j in range(len(df_closeness_centrality)) :
        if int(df_closeness_centrality.node[j]) == target :
            df_graph.loc[i] = [df_graph.node[i], df_graph.popularity[i], df_graph.C_deg[i], df_graph.pagerank[i], df_graph.C_btw[i], df_graph.C_eigen[i], int(df_closeness_centrality.closeness_centrality[j] * 1000000)]



## 3. 샘플데이터 추출 => Train(7) : Test(3)
df_predict = pd.DataFrame(columns=['node', 'popularity', 'C_deg', 'pagerank', 'C_btw', 'C_eigen', 'C_close'])
df_sample = pd.DataFrame(columns=['node', 'popularity', 'C_deg', 'pagerank', 'C_btw', 'C_eigen', 'C_close'])
df_train = pd.DataFrame(columns=['node', 'popularity', 'C_deg', 'pagerank', 'C_btw', 'C_eigen', 'C_close'])
df_test = pd.DataFrame(columns=['node', 'popularity', 'C_deg', 'pagerank', 'C_btw', 'C_eigen', 'C_close'])

for i in range(len(df_graph)) :
    if int(df_graph.popularity[i]) != 0 :
        df_sample.loc[len(df_sample)] = [df_graph.node[i], df_graph.popularity[i], df_graph.C_deg[i], df_graph.pagerank[i], df_graph.C_btw[i], df_graph.C_eigen[i], df_graph.C_close[i]]
    elif int(df_graph.popularity[i]) == 0 :
        df_predict.loc[len(df_predict)] = [df_graph.node[i], df_graph.popularity[i], df_graph.C_deg[i], df_graph.pagerank[i], df_graph.C_btw[i], df_graph.C_eigen[i], df_graph.C_close[i]]

sample = np.array(range(200)).tolist()
train_index=[]                          
for i in range(140):
    a = random.randint(0,199)       
    while a in train_index :              # 중복방지
        a = random.randint(0,199)
    train_index.append(a)

for i in range(len(train_index)) :
    sample.remove(train_index[i])

test_index = sample

train_index.sort()
test_index.sort()

for idx in train_index :
    df_train.loc[len(df_train)] = [df_sample.node[idx], df_sample.popularity[idx], df_sample.C_deg[idx], df_sample.pagerank[idx], df_sample.C_btw[idx], df_sample.C_eigen[idx], df_sample.C_close[idx]]

for idx in test_index :
    df_test.loc[len(df_test)] = [df_sample.node[idx], df_sample.popularity[idx], df_sample.C_deg[idx], df_sample.pagerank[idx], df_sample.C_btw[idx], df_sample.C_eigen[idx], df_sample.C_close[idx]]



# ## 4. Training and make model
train_case = []
train_label = []

for i in range(len(df_train)) :
    temp = []
    temp.append(df_train.C_deg[i])
    temp.append(df_train.pagerank[i])
    temp.append(df_train.C_btw[i])
    # temp.append(df_train.C_eigen[i])
    temp.append(df_train.C_close[i])
    
    train_case.append(temp)

    if int(df_train.popularity[i]) == -1 :
        temp_res = 0
    elif int(df_train.popularity[i]) == 1 :
        temp_res = 1
    train_label.append(temp_res)

X = np.array(train_case)
y = np.array(train_label)

model=Sequential()
model.add(Dense(1, input_dim=4, activation='sigmoid'))
sgd=optimizers.SGD(lr=0.01)
model.compile(optimizer='sgd' ,loss='binary_crossentropy',metrics=['binary_accuracy'])      # sgd는 경사 하강법을 의미. # 손실 함수(Loss function)는 binary_crossentropy(이진 크로스 엔트로피)를 사용합니다.
model.fit(X,y, batch_size=1, epochs=100, shuffle=False)     # 주어진 X와 y데이터에 대해서 오차를 최소화하는 작업을 800번 시도합니다.



## 5. Data Test

test_case = []
test_label = []

for i in range(len(df_test)) :
    temp = []
    temp.append(df_test.C_deg[i])
    temp.append(df_test.pagerank[i])
    temp.append(df_test.C_btw[i])
    # temp.append(df_test.C_eigen[i])
    temp.append(df_test.C_close[i])

    test_case.append(temp)

    if int(df_train.popularity[i]) == -1 :
        temp_res = 0
    elif int(df_train.popularity[i]) == 1 :
        temp_res = 1
    test_label.append(temp_res)

X = np.array(test_case)

predict_list = model.predict(X).tolist()

df_test_res = pd.DataFrame(columns=['node', 'popularity', 'predict', 'correct'])

for i in range(len(predict_list)) :
    if predict_list[i][0] >= 0.5 :
        res_predict = 1
    else :
        res_predict = -1
    
    if int(df_test.popularity[i]) == res_predict :
        correct = 1
    else : 
        correct = 0
    df_test_res.loc[i] = [df_test.node[i], int(df_test.popularity[i]), res_predict, correct]

correct_cnt = df_test_res['correct'].sum()

print("correct : ", correct_cnt)
acc_ratio = round((correct_cnt / len(df_test)), 2) * 100
print("정답률 : ", acc_ratio, '%')


## 6. predict
predict_case = []

for i in range(len(df_predict)) :
    temp = []
    temp.append(df_predict.C_deg[i])
    temp.append(df_predict.pagerank[i])
    temp.append(df_predict.C_btw[i])
    # temp.append(df_predict.C_eigen[i])
    temp.append(df_predict.C_close[i])
    
    predict_case.append(temp)

X = np.array(predict_case)

predict = model.predict(X).tolist()

df_predict_res = pd.DataFrame(columns=['node', 'predict'])

final_res = ''

for i in range(len(predict)) :
    if predict[i][0] >= 0.5 :
        res_predict = 1
    else :
        res_predict = -1
    
    df_predict_res.loc[i] = [df_predict.node[i], res_predict]

    if i == (len(predict)-1) :
        final_res = final_res + str(int(df_predict.node[i])) + '\t' + str(res_predict)
    else :
        final_res = final_res + str(int(df_predict.node[i])) + '\t' + str(res_predict) + '\n'

## write result
filename = "result_kimsuyoung.txt"
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print(final_res)

sys.stdout = sys.__stdout__
f.close()