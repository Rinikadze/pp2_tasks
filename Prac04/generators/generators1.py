def square_generator(n):
    for i in range(n + 1):
        yield i * i

n = int(input())
for i in square_generator(n):
    print(i)