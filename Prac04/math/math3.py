import math

n = int(input("Input number of sides: "))
side = float(input("Input the length of a side: "))

area = (n * side ** 2) / (4 * math.tan(math.pi / n))
print("The area of the polygon is:", area)