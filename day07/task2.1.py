def filter_by_length(words, n):
    result = []

    for word in words:
        if len(word) == n:
            result.append(word)

    return result


words = ["cat", "dog", "bird", "apple", "car", "house"]

print(filter_by_length(words, 3))
print(filter_by_length(words, 4))


def filter_letters_only(words):
    result = []

    for word in words:
        if word.isalpha():
            result.append(word)

    return result


words = [
    "cat",
    "dog",
    "hello2",
    "hello-world",
    "hello world",
    "bird"
]

print(filter_letters_only(words))


def group_by_length(words):
    result = {}

    for word in words:
        length = len(word)

        if length not in result:
            result[length] = []

        result[length].append(word)

    return result


words = ["cat", "dog", "bird", "apple", "car"]

print(group_by_length(words))


import random


def filter_by_length(words, n):
    result = []

    for word in words:
        if len(word) == n:
            result.append(word)

    return result


words = ["cat", "dog", "bird", "apple", "house", "car"]

length = int(input("Enter word length: "))

matching_words = filter_by_length(words, length)

if len(matching_words) == 0:
    print("No words found.")
else:
    random_word = random.choice(matching_words)
    print("Random word:", random_word)