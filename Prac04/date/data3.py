from datetime import datetime

now = datetime.now()

formatted = now.strftime("%Y-%m-%d %H:%M:%S")

print("Original:", now)
print("Without microsec:", formatted)