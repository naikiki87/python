from sklearn.datasets import make_moons
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import mglearn
import numpy as np

X, y = make_moons(n_samples=200, noise=0.05, random_state=0)

scaler = StandardScaler()
scaler.fit(X)

X_scaled = scaler.transform(X)

# print(X)
print(X_scaled)

# # dbscan = DBSCAN()
# dbscan = DBSCAN(eps=0.7)
# clusters = dbscan.fit_predict(X_scaled)

# # plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=clusters, cmap=mglearn.cm2, s=60, edgecolors='black')
# # plt.xlabel("attr 0")
# # plt.ylabel("attr 1")
# # plt.show()

# # plt.plot([2,3,4],[4,6,9], c="yellow")
# # plt.show()