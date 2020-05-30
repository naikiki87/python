from sklearn.cluster import DBSCAN
from sklearn import datasets
import pandas as pd
import matplotlib.pyplot  as plt
import seaborn as sns

iris = datasets.load_iris()

labels = pd.DataFrame(iris.target)
labels.columns=['labels']
data = pd.DataFrame(iris.data)
data.columns=['Sepal length','Sepal width','Petal length','Petal width']
data = pd.concat([data,labels],axis=1)

print(data.head())

feature = data[ ['Sepal length','Sepal width','Petal length','Petal width']]
print(feature.head())

model = DBSCAN(eps=0.3,min_samples=6)
predict = pd.DataFrame(model.fit_predict(feature))
predict.columns=['predict']

print(predict.head())

r = pd.concat([feature,predict],axis=1)

print(r)

feature = data[ ['Sepal length','Sepal width']]

sns.jointplot(x="Sepal length", y="Sepal width", data=feature, kind="kde")
plt.suptitle("꽃받침의 길이와 넓이의 Joint Plot 과 Kernel Density Plot", y=1.02)
plt.show()

# sns.pairplot(r,hue='predict')
# plt.show()

# from mpl_toolkits.mplot3d import Axes3D
# # scatter plot
# fig = plt.figure( figsize=(6,6))
# ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
# ax.scatter(r['Sepal length'],r['Sepal width'],r['Petal length'],c=r['predict'],alpha=0.5)
# ax.set_xlabel('Sepal lenth')
# ax.set_ylabel('Sepal width')
# ax.set_zlabel('Petal length')
# plt.show()

##### EVALUATE MODEL WITH CROSS TABULIZATION #####
# ct = pd.crosstab(data['labels'],r['predict'])
# print (ct)

##### STANDARIZE VALUE #####

# from sklearn.pipeline import make_pipeline
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import DBSCAN

# scaler = StandardScaler()
# model = model = DBSCAN(min_samples=6)
# pipeline = make_pipeline(scaler,model)
# predict = pd.DataFrame(pipeline.fit_predict(feature))
# predict.columns=['predict']

# # concatenate labels to df as a new column
# r = pd.concat([feature,predict],axis=1)

# ct = pd.crosstab(data['labels'],r['predict'])
# print (ct)