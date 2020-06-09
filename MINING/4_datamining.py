from sklearn.cluster import DBSCAN
from sklearn import datasets
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt
import seaborn as sns

rawdata = pd.read_csv('total.txt', sep = "\t", names=['timestamp', 'data', 'id', 'x', 'y'])


feature = rawdata[['timestamp', 'x', 'y']]
# feature = rawdata[['id', 'x', 'y']]

print(feature.head(10))

# model = DBSCAN(eps=1, min_samples=3)

# cluster = pd.DataFrame(model.fit_predict(feature))
dbscan = DBSCAN(eps=0.5, min_samples=2)
cluster = dbscan.fit_predict(feature)
print("unique label : ", np.unique(cluster))

# cluster.columns=['cluster']
# data = pd.concat([feature, cluster],axis=1)
# print(data)

plt.scatter(feature['x'], feature['y'], c=cluster, s=5)
plt.show()

# plt.scatter()

# plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=clusters, cmap=mglearn.cm2, s=60, edgecolors='black')

# plt.scatter(data['cluster'], data['cluster'])
# plt.show()