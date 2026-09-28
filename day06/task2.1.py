def sum_to(n):
    if n == 1:
        return 1
    return n + sum_to(n - 1)
 
print(sum_to(42))