def count_types(word):
    vowels = 0
    consonants = 0

    word = word.lower()

    for character in word:
        if character.isalpha():
            if character in "aeiou":
                vowels += 1
            else:
                consonants += 1

    print(vowels, "vowels,", consonants, "consonants")


count_types("Hello World!")
count_types("Python")
count_types("Hello123!!!")