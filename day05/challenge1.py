import random
import time

start = time.time()
big_list = [random.randint(0, 1000000) for i in range(1000000)]
big_list.sort()
print(time.time() - start)