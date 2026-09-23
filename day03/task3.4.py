text_input=input("enter a sentence:")
words = text_input.split()
new_word=""
for i in range(len(words)):
    new_word+=words[i][0]

print(new_word)

#split() function splits the strings in the spaces and put each word into the list.