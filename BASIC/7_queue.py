from collections import deque

items = deque()

for i in range(10) :
    if i > 5 :
        items.pop()
    items.appendleft(i)
    print(items)
    print(len(items))


print(sum(items))

