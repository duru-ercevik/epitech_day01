import random
from english_words import get_english_words_set
import time  

NUMBERS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"] #in order to print the numbers in letters


def check_lose(penalties): #to check if the penalty limit is exceeded or not
    if penalties >= MAX_PENALTIES:
        print("You lose!")
        return True #if the user lost return true 
    return False


def pick_word(): #picking a random english word
    words = get_english_words_set(['web2'], lower=True)
    return random.choice(list(words)).upper()


def hidden_word(word, found_letters): #printing the _ sign as many times the word has and if the user guess the letter correct replace the _ by the letter
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
    start_time = time.time()

    print(hidden_word(word, found_letters) + "/ " + penalty_text(penalties))

    while True:
        guess = input("\n$> ").upper()
        if time.time() - start_time > TIME_LIMIT:
            print("Time's up! You lose! The word was " + word)
            return

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

        print("Time left: " + str(int(TIME_LIMIT - (time.time() - start_time))) + " seconds")

MAX_PENALTIES = int(input("Set a penalty limit: "))
TIME_LIMIT = int(input("Set a time limit: "))

play()