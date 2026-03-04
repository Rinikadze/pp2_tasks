from datetime import datetime

a = datetime(2026, 3, 1, 12, 0, 0)
b = datetime(2026, 3, 5, 15, 30, 0)

dif = b - a
res = dif.total_seconds()

print("Difference in seconds:", res)