temp = []

for i in range(5) :
    print(i)
    item = "item" + str(i)
    temp.append(item)
    # print(globals()['item{}.format(i)'])
    # item = globals()['item{}.format(i)']
    # temp.append(item)

print(temp)