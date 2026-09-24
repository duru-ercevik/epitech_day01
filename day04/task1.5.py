number = int(input("enter an integer:"))

found = False

if number == 42:
    print("a" , end="")
    found = True

if number <= 21:
    print("b" , end="")
    found = True

if number % 2 == 0:
    print("c", end="")
    found = True

if number / 2 < 21:
    print("d", end="")
    found = True

if number % 2 == 1 and number >= 45:
    print("e", end="")
    found = True

if found==False:
    print("f")