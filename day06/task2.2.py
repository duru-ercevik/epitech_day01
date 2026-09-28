def is_palindrome(text):
    if len(text) <= 1:
        return True
    if text[0] != text[-1]:
        return False
    return is_palindrome(text[1:-1])
 
def palindrome():
    text = input("Enter a string: ")
    cleaned = ""
    for c in text.lower():
        if c.isalnum():
            cleaned += c
    return is_palindrome(cleaned)
 
print(palindrome())