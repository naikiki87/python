import pandas as pd

# df = pd.DataFrame(columns = ['code'])

for i in range(2):
    globals()['variable{}'.format(i)] = pd.DataFrame(columns = ['code', 'price'])

# variable0.loc[0] = ["1234"]
# variable1.loc[0] = ["1234"]

for j in range(2):
    globals()['variable{}'.format(j)].loc[0] = ['1234', 3456]
    # variable{}.format(j).loc[0] = ["1234"]

for k in range(2):
    print(globals()['variable{}'.format(j)]['price'])
# print(variable0)
# print(variable1)