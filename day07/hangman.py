import random
from english_words import get_english_words_set

MAX_PENALTIES = 12
NUMBERS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def check_lose(penalties):
    if penalties >= MAX_PENALTIES:
        print("You lose!")
        return True
    return False


def pick_word():
    words = get_english_words_set(['web2'], lower=True)
    return random.choice(list(words)).upper()


def hidden_word(word, found_letters):
    result = ""
    for letter in word:
        if letter in found_letters:
            result += letter + " "
        else:
            result += "_ "
    return result


def penalty_text(penalties):
    if penalties > 1:
        return str(penalties) + " penalties"
    return str(penalties) + " penalty"


def play():
    word = pick_word()
    found_letters = []
    penalties = 0

    print(hidden_word(word, found_letters) + "/ " + penalty_text(penalties))

    while True:
        guess = input("\n$> ").upper()

        if not guess.isalpha():
            print("Please type letters only.")
            continue

        if len(guess) == 1:
            if guess in found_letters:
                print("You already tried '" + guess + "'")
            elif guess in word:
                found_letters.append(guess)
                count = word.count(guess)
                print("Found " + NUMBERS[count] + " '" + guess + "'")
            else:
                found_letters.append(guess)
                penalties += 1
                print("No '" + guess + "' found")
        else:
            if guess == word:
                print(guess + ": correct guess - " + penalty_text(penalties))
                return
            penalties += 5
            print(guess + ": incorrect guess")

        if "_" not in hidden_word(word, found_letters):
            print(word + ": you found it! - " + penalty_text(penalties))
            return

        if check_lose(penalties):
            print("The word was " + word)
            return

        print(hidden_word(word, found_letters) + "/ " + penalty_text(penalties))


play()