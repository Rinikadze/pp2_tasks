import os

os.makedirs("test/move")
with open("test/example.txt", "w") as f:
    f.write("Hello")

a = os.listdir("test")
print(a)

for f in os.listdir("test"):
    if f.endswith(".txt"):
        print("Found:", f)