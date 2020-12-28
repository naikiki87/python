import pandas as pd

temp1 = pd.DataFrame(columns=['tid', 'uid', 'iid'])
temp2 = pd.DataFrame(columns=['pid', 'iid'])

temp1.loc[0] = [1, 1, 1]
temp1.loc[1] = [1, 1, 2]

temp2.loc[0] = [10, 3]
temp2.loc[1] = [10, 4]
temp2.loc[2] = [10, 5]

print(temp1)
print(temp2)

df_merge = pd.merge(temp1, temp2, how="right", on="iid")
print(df_merge)