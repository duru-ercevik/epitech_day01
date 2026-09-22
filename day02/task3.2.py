number=0
for i in range(10):
    number+=i

print(number)

number2=0
for a in range(1,10):
    number2+=2*a

print(number2)

number3=123456789 * 987654321
number_3=0
for k in str(number3):
    number_3+=int(k)
print(number_3)