from datetime import datetime

a = datetime.now()

b = a.strftime("%Y-%m-%d %H:%M:%S")

print("Original:", a)
print("Without microsec:", b)