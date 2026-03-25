from functools import reduce

a = [1, 2, 3, 4, 5]
b = list(map(lambda x: x + 10, a))
c = list(filter(lambda x: x % 2 == 0, a))
d = reduce(lambda x, y: x + y, a)