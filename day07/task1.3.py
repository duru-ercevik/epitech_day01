def is_anagram(word1, word2):
    word1 = word1.lower()
    word2 = word2.lower()

    if len(word1) != len(word2):
        return False

    frequency1 = {}
    frequency2 = {}

    for character in word1:
        if character in frequency1:
            frequency1[character] += 1
        else:
            frequency1[character] = 1

    for character in word2:
        if character in frequency2:
            frequency2[character] += 1
        else:
            frequency2[character] = 1

    return frequency1 == frequency2


print(is_anagram("listen", "silent"))
print(is_anagram("hello", "world"))
print(is_anagram("listen", "silentx"))