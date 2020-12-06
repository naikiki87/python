import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

"""
- radius 리스트를 입력받아서, 각 반지름의 원에 위치하는 n개의 샘플을 뽑아서 x, y 리스트들을 리턴해줍니다. 
"""
def return_circle_xy(rs, n):
    xs, ys = [], []
    for r in rs:
        for i in range(0, n):
            angle = np.pi * np.random.uniform(0, 2)
            xs.append( r*np.cos(angle) + np.random.random())
            ys.append( r*np.sin(angle) + np.random.random())
    return xs, ys

x, y = return_circle_xy([10, 5], 500)
df = pd.DataFrame({"x":x, "y":y})

from sklearn.cluster import SpectralClustering, AgglomerativeClustering

f, axes = plt.subplots(1, 2, sharex=True, sharey=True)
f.set_size_inches((10, 4)) 

# spectral clustering and scattering
CluNums = SpectralClustering(n_clusters=2, n_init=10).fit_predict(df)
axes[0].scatter(x, y, c=CluNums, cmap=plt.cm.rainbow, alpha=0.3)
axes[0].set_title("Spectral Clustering")

# agglomerative clustering and scattering
CluNums = AgglomerativeClustering(n_clusters=2).fit_predict(df)
axes[1].scatter(x, y, c=CluNums, cmap=plt.cm.rainbow, alpha=0.3)
axes[1].set_title("Agglomerative Clustering")

# plt.savefig('../../assets/images/markdown_img/spec_agg_clustering_18051202105.svg')
plt.show()