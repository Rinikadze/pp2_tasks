from datetime import datetime, timedelta

a = datetime.now()
b = a - timedelta(days=1)
c = a + timedelta(days=1)

print("Yesterday:", b)
print("Today:", a)
print("Tomorrow:", c)