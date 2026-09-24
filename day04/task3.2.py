user_text=input("enter a text:")
key=int(input("enter the hey value:"))
decrypted = ""

for char in user_text:
    if char.isalpha():
        position = ord(char.lower()) - ord("a")
        new_position = (position - key) % 26
        new_char = chr(new_position + ord("a"))
        decrypted += new_char
    else:
        decrypted += char

print(decrypted)