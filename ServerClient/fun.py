duplicats = {"hej": 3, " ": 1, "c": 0, " med ": 10, " dig ": 2}

result = ""
for keys in duplicats:
    for numberTimes in range(0, int(duplicats[keys])):
        result += keys

print(result)