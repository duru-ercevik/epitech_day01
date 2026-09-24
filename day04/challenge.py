number = int(input("enter an integer:"))
text = input("enter a text:")

if number == 0:
    quit()

if any(char in "aeiou" for char in text):
    print(number)
elif number >= 42:
    print(number)
else:
    print(text)