user_text=input("enter a text:")
key=int(input("enter the hey value:"))

encrypted = ""

for char in user_text:
    if char.isalpha(): #to check if it is a letter or not
        position = ord(char.lower()) - ord("a") #to find the location in the alphabet we need to subtract from a (starting point)
        new_position = (position + key) % 26 #finding the new position
        new_char = chr(new_position + ord("a")) #turning it into character
        encrypted += new_char #adding it to our string
    else:
        encrypted += char #do not change if it space or soething else than letters

print(encrypted)

#ord() function is used to turn the characters into number and chr() function does the reverse 