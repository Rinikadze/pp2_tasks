def even(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input())
print(", ".join(str(i) for i in even(n)))