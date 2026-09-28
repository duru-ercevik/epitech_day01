import os
import time

def fast_power(base, exponent):
    result = 1
    while exponent > 0:
        if exponent % 2 == 1:
            result = result * base
        base = base * base
        exponent = exponent // 2
    return result

    
for exponent in [84, 168]:
    start = time.perf_counter()
    fast_power(42, exponent)
    print("fast 42^" + str(exponent) + ":", time.perf_counter() - start)    