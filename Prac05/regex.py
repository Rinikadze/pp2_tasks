import re

with open("raw.txt", "r", encoding="utf-8") as f:
    a = f.read()

b = re.findall(r"ab*", a)
print(b)

c = re.findall(r"ab{2-3}", a)
print(c)

d = re.findall(r"[a-z]+_[a-z]+", a)
print(d)

e = re.findall(r"[A-Z][a-z]+", a)
print(e)

f = re.findall(r"a.*b", a)
print(f)

g = re.sub(r"[\., ]", ":", a)
print(g)

h = re.sub(r"_([a-z])", lambda x: x.group(1).upper(), a)
print(h)

i = re.split(r"(?=[A-Z])", a)
print(i)

j = re.sub(r"([A-Z])", lambda x: (" " + x.group(1).lower()).strip(), a)
print(j)

k = re.sub(r"(?<=.)([A-Z])", lambda x: "_" + x.group(1).lower(), a)
print(k)