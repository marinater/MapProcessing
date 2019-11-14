import random
from math import pi

outcomes = {}
n = 100000
for i in range(n):
    a = 100
    b = 100

    while a > 0 and b > 0:
        val = random.randint(0,1)
        if val == 0:
            a -= 1
        else:
            b -= 1

    remaining = a+b
    if remaining in outcomes:
        outcomes[remaining] += 1
    else:
        outcomes[remaining] = 1

e = 0
for x,y in outcomes.items():
    e += x * y

e /= n

a_e = (2 * (100 / pi) ** (1/2)) - 1
print('actual E:', e)
print('expected E:', a_e)
# [ print(x,':',y) for x,y in sorted(outcomes.items()) ]
