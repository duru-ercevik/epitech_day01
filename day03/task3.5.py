text = input("Enter a text: ")

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


# freq of English 
english = {
    "e": 12.7,
    "t": 9.1,
    "a": 8.2,
    "o": 7.5,
    "i": 7.0,
    "n": 6.7
}


# freq of French
french = {
    "e": 14.7,
    "a": 7.6,
    "i": 7.5,
    "n": 7.1,
    "o": 5.8,
    "r": 6.6
}


# freq of Turkish
turkish = {
    "e": 8.9,
    "a": 8.5,
    "i": 8.0,
    "n": 7.0,
    "r": 6.7,
    "s": 3.0
}


# diff with English 
english_difference = 0 #starting with the 0

for letter in english: #visitig letters in english
    user_value = user_frequency.get(letter, 0) #we are looking the freq of letter of the input and if we don't have that letter in the input put 0 for it
    language_value = english[letter] #we take the value for that letter for english

    english_difference += abs(user_value - language_value) #adding the difference for all letters


# diff with French 
french_difference = 0

for letter in french:
    user_value = user_frequency.get(letter, 0)
    language_value = french[letter]

    french_difference += abs(user_value - language_value)


# diff with Turkish
turkish_difference = 0

for letter in turkish:
    user_value = user_frequency.get(letter, 0)
    language_value = turkish[letter]

    turkish_difference += abs(user_value - language_value)


# keeping the results in the dictionary
differences = {
    "English": english_difference,
    "French": french_difference,
    "Turkish": turkish_difference
}


language = min(differences, key=differences.get) #choosing the smallest difference

print("English difference:", english_difference)
print("French difference:", french_difference)
print("Turkish difference:", turkish_difference)

print("The estimated language is:", language)