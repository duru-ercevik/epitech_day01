# Tablodaki Ingilizce harf frekanslari (%)
FREQ = {
    'a': 8.2, 'b': 1.5, 'c': 2.8, 'd': 4.3, 'e': 12.7, 'f': 2.2, 'g': 2.0,
    'h': 6.1, 'i': 7.0, 'j': 0.15, 'k': 0.8, 'l': 4.0, 'm': 2.4, 'n': 6.7,
    'o': 7.5, 'p': 1.9, 'q': 0.1, 'r': 6.0, 's': 6.3, 't': 9.1, 'u': 2.8,
    'v': 1.0, 'w': 2.4, 'x': 0.15, 'y': 2.0, 'z': 0.07
}
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

cipher = input("Encrypted text: ")
key_length = int(input("Key length: "))

# 1) Anahtari bul
letters = [c for c in cipher.lower() if c in ALPHABET] #make the continuous string get rid of spaces
key = "" #creates an empty string and add the letters one by one
for i in range(key_length): 
    column = letters[i::key_length] #grouping the letters that are encrypted with the same key letter
    best_shift = 0 #in order to keep the best shift and score
    best_score = 0
    for shift in range(26): #we are trying for every letter in alphabet
        score = 0
        for c in column:
            decrypted = ALPHABET[(ALPHABET.index(c) - shift) % 26] #shifting the letter by "shift"
            score += FREQ[decrypted] #summing the freq for all the group and keep a score
        if score > best_score:
            best_score = score
            best_shift = shift #we are keeping the best shift here 
    key += ALPHABET[best_shift] #we are adding to the key one by one until the key_lenght
print("Key:", key)

result = ""
j = 0 #keeping which index we are in with the key
for c in cipher.lower():
    if c in ALPHABET: #if it is a letter shift it with the according key letter
        shift = ALPHABET.index(key[j % key_length])
        result += ALPHABET[(ALPHABET.index(c) - shift) % 26]
        j += 1
    else:
        result += c
print("Clear text:", result)