import codecs

text = input("Enter a text: ")

# Convert the input text to UTF-8
text = codecs.decode(text.encode("utf-8"), "utf-8")

text = text.lower()

letter_counts = {}

for char in text:
    if char.isalpha():
        if char in letter_counts:
            letter_counts[char] += 1
        else:
            letter_counts[char] = 1

total_letters = sum(letter_counts.values())

user_frequency = {}

for letter in letter_counts:
    frequency = letter_counts[letter] / total_letters * 100
    user_frequency[letter] = frequency

    print(letter, frequency)


english = {
    "e": 12.7,
    "t": 9.1,
    "a": 8.2,
    "o": 7.5,
    "i": 7.0,
    "n": 6.7
}

french = {
    "e": 14.7,
    "a": 7.6,
    "i": 7.5,
    "n": 7.1,
    "o": 5.8,
    "r": 6.6
}

turkish = {
    "e": 8.9,
    "a": 8.5,
    "i": 8.0,
    "n": 7.0,
    "r": 6.7,
    "s": 3.0
}


english_difference = 0

for letter in english:
    user_value = user_frequency.get(letter, 0)
    language_value = english[letter]

    english_difference += abs(user_value - language_value)


french_difference = 0

for letter in french:
    user_value = user_frequency.get(letter, 0)
    language_value = french[letter]

    french_difference += abs(user_value - language_value)


turkish_difference = 0

for letter in turkish:
    user_value = user_frequency.get(letter, 0)
    language_value = turkish[letter]

    turkish_difference += abs(user_value - language_value)


differences = {
    "English": english_difference,
    "French": french_difference,
    "Turkish": turkish_difference
}


language = min(differences, key=differences.get)


print()
print("English difference:", english_difference)
print("French difference:", french_difference)
print("Turkish difference:", turkish_difference)

print()
print("Estimated language:", language)