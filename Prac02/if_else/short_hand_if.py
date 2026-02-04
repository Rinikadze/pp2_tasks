a = 5
b = 2
if a > b: print("a is greater than b")

a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger)

x = 15
y = 20
max_value = x if x > y else y
print("Maximum value:", max_value)

username = ""
display_name = username if username else "Guest"
print("Welcome,", display_name)