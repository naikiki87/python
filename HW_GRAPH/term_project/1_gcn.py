import numpy as np
import pickle as pkl #serialize를 위한 바이너리 프로토콜 구현. 클래스를 통째로 저장 및 불러올 때 유용하다.
import networkx as nx #그래프를 다루기 위한 파이썬 패키지
import scipy.sparse as sp #행렬의 대부분의 원소가 0인 sparse matrix를 만들기 위해 불러온다
from scipy.sparse.linalg.eigen.arpack import eigsh #대칭행렬에서 k개의 eigen vector와 eigen value를 가져옴 
import sys
import torch
from torch import nn
from torch import optim
from torch.nn import functional as F
import numpy as np
import easydict
 
#easydict를 이용해 hyperparameter 및 사용할 데이터를 미리 정의한다.
args = easydict.EasyDict({'dataset': 'pubmed',
                          'model': 'gcn',
                          'learning_rate': 0.01,
                          'epochs': 400,
                          'hidden': 16,
                          'dropout': 0.5,
                          'weight_decay' : 5e-4,
                          'early_stopping':10,
                          'max_degree' : 3
                         })
 
 
 
names = ['x', 'y', 'tx', 'ty', 'allx', 'ally', 'graph']
objects = []
 
for i in range(len(names)): #각 파일들을 열고 pickle모듈을 이용해 serialized된 데이터를 파싱한다.
    with open("data/ind.{}.{}".format(args.dataset, names[i]), 'rb') as f:
        objects.append(pkl.load(f, encoding='latin1'))
 
print(len(objects)) #7이 잘 나온다.
 
 
def parse_index_file(filename): #테스트데이터의 index를 담고 있는 파일을 파싱하기 위한 함수
    index = []
    for line in open(filename):
        index.append(int(line.strip()))
        
    return index
 
 
 
x, y, tx, ty, allx, ally, graph = tuple(objects) #튜플로 변환하고 7개의 데이터를 나눈다.
 
 
test_idx_reorder = parse_index_file("data/ind.{}.test.index".format(args.dataset))
test_idx_range = np.sort(test_idx_reorder) #테스트데이터의 index를 오름차순 정렬한다. 
 
 
 
features = sp.vstack((allx, tx)).tolil() #train데이터와 테스트데이터를 하나의 matrix로 결합하고 LInked List format으로 변환
 
 
 
features[test_idx_reorder, :] = features[test_idx_range, :] #테스트 데이터의 인덱스를 이용해 테스트 데이터를 전체 메트릭스 안에서 재배치 한다 
adj = nx.adjacency_matrix(nx.from_dict_of_lists(graph)) #node list를 받아 adjacency matrix를 만들어주는 함수이다.
 
labels = np.vstack((ally, ty)) # 전체 레이블 데이터를 하나의 matrix로 만든다.
 
labels[test_idx_reorder, :] = labels[test_idx_range, :] #테스트데이터의 인덱스를 이용해 테스트 레이블 데이터를 전체 레이블 matrix에서 재배치한다
 
idx_test = test_idx_range.tolist()
idx_train = range(len(y))
idx_val = range(len(y), len(y)+500)
 
'''
이렇게 train, test, validation 데이터 나누기를 위한 준비가 완성되었다.
'''
 
 
def sample_mask(idx, l): #마스크를 만드는 함수
#주어진 데이터가 마스킹이 되어있지 않은 상태이기 때문에 따로 마스킹이 필요하다.
    

    mask = np.zeros(l) # ㅣ차원의 벡터를 만들고 0으로 채운다. 
    mask[idx] = 1 # 0벡터의 idx 자리에 1을 넣는다. 0은 마스킹을 하는 것이고 1은 마스킹을 하지 않는 것이다.
    

    return np.array(mask, dtype=np.bool)
 
num_of_labels = labels.shape[0] #19717개의 레이블이 있다.
        
train_mask = sample_mask(idx_train, num_of_labels)
val_mask = sample_mask(idx_val, num_of_labels)
test_mask = sample_mask(idx_test, num_of_labels)
 
 
 
y_train = np.zeros(labels.shape) #labels.shape는 (19717, 3) 이다.
y_val = np.zeros(labels.shape)
y_test = np.zeros(labels.shape)
 
#label data를 마스킹한 후 재구성한다. Semi-Supervised이기 때문에 마스킹을 해주는 것이다.


 
y_train[train_mask, :] = labels[train_mask, :]
y_val[val_mask, :] = labels[val_mask, :]
y_test[test_mask, :] = labels[test_mask, :]
 
 
seed = 123
np.random.seed(seed)
torch.random.manual_seed(seed)
 
#이제 차원이 제대로 맞추어져 있는지 확인해보자
print('adj:', adj.shape)
print('features:', features.shape)
print('y:', y_train.shape, y_val.shape, y_test.shape)
print('mask:', train_mask.shape, val_mask.shape, test_mask.shape)