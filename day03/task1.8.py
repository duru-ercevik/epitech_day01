p = "abcdefghij"
print(p[::-2][:5][::-1][3:])

#[::-2] --> jhfdb  reverse it and print 1 and skip 1
#[::-2][:5] --> jhfdb take the first 5 character
#[::-2][:5][::-1] --> bdfhj reverse the string
#[::-2][:5][::-1][3:] --> hj print the string starting the index 3