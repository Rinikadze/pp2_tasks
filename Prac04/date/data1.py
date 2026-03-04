from datetime import datetime, timedelta

a = datetime.now()
b = a - timedelta(days=5)

print("Current date:", a)
print("5 days earlier:", b)