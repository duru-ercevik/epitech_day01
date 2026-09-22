number = 1

for number in range(1, 1000000000):
    divisible = True

    for divisor in range(1, 21):
        if number % divisor != 0:
            divisible = False
            break

    if divisible:
        print(number)
        break

    number += 1

