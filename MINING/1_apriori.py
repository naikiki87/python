import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

f=open('test.txt', mode='wt', encoding='utf-8')

f.write('file write with python\n')
f.write('file write with python2\n')
f.write('file write with python3\n')

f.close()

r=open('test.txt', mode='rt', encoding='utf-8')

temp = r.readlines()

print(temp[0])
site = temp[0].split(" ")

print(site)

dataset=[site,
['Apple','Cheese','Water'],
['Water','Walnut','Cheese','Salmon'],
['Melon','Apple','Water'],
['Water','Walnut','Cheese','Corn']]

te = TransactionEncoder()
te_ary = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_ary, columns=te.columns_)

print(df)

frequent_itemsets = apriori(df, min_support=0.4, use_colnames=True)
print(frequent_itemsets)