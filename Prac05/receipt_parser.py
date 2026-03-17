import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    a = f.read()

prices = re.findall(r"Стоимость\n(\d+,\d+)", a)

names = re.findall(r"\d+\.\n(.+)\n", a)

total = re.findall(r"ИТОГО:\n(\d+\s\d+,\d+)", a)

date_time = re.findall(r"Время: (\d+\.\d+\.\d+ \d+:\d+:\d+)", a)
b = date_time[0].split()
date = b[0]
time = b[1]

payment = re.findall(r"\w* карта", a)

data = {
    "prices": prices,
    "products": names,
    "total": total,
    "date": date,
    "time": time,
    "payment_method": payment
}

c = json.dumps(data, ensure_ascii=False, indent=2)
print(c)