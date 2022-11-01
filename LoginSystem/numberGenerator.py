from random import randint

file = open("nunber.py", "w")
num = []
for i in range(0, 1000):
    num.append(randint(-200, 200))
file.write(str(num))
