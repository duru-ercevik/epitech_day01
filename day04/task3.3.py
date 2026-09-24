message = input("Enter a message: ")
key = input("Enter a key: ")

encrypted = ""
key_index = 0

for char in message:
    if char.isalpha():

        position = ord(char.lower()) - ord("a")  #turning the letter into number with respect to a

        key_position = ord(key[key_index % len(key)].lower()) - ord("a")  #it makes the continuous key (key_index % len(key)) and turns the letters of key to the number

        new_position = (position + key_position) % 26 #finding the new position

        new_char = chr(new_position + ord("a")) #turning the number to the character

        encrypted += new_char

        key_index += 1 

    else:
        encrypted += char

print("encrypted text is:"+encrypted)


decrypted = ""
key_index = 0

for char in encrypted:
    if char.isalpha():

        position = ord(char.lower()) - ord("a")

        key_position = ord(key[key_index % len(key)].lower()) - ord("a")

        new_position = (position - key_position) % 26

        new_char = chr(new_position + ord("a"))

        decrypted += new_char

        key_index += 1

    else:
        decrypted += char

print("decrypted text is:"+decrypted)