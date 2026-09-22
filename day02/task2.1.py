number = 0
result = 0

for i in range(9):
    number = number * 10 + 1
    result = result + number

for power in range(2, 6):
    print(result ** power)

for i in range(9, 11):
    number = number * 10 + 1
    result = result + number

    print(result)

    for power in range(2, 6):
        print(result ** power)