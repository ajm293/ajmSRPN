# Python implementation of GLIBC rand() function
# Alexander Morrison, 2020
# Attrib: https://www.gnu.org/software/libc/ under GNU GPL license
# Documentation used: https://www.mscs.dal.ca/~selinger/random/
# Also used: https://stackoverflow.com/questions/18634079/glibc-rand-function-implementation
# which references: https://sourceware.org/git/?p=glibc.git;a=blob;f=stdlib/random_r.c;hb=glibc-2.15#l361

# Initialisation script based off of documentation.

seed = 1  # This is the seed that SRPN uses by inspection
n = 344  # Index where the random values will eventually be taken from
MAX = 1000  # Index+1 where the generator stops
randArray = []
randArray.append(seed)  # Initialise list r with the seed (r0 in docs)
for i in range(1, 31):  # ri for i=1...30 in docs
    gen = (16807 * randArray[i-1]) % 2147483647
    randArray.append(gen)
    if randArray[i] < 0:
        randArray[i] += 2147483647
for i in range(31,34):  # ri for i=31...33
    gen = randArray[i-31]
    randArray.append(gen)
for i in range(34,MAX):  # ri for i>=34 in docs, here we generate up to 1000.
    gen = (randArray[i-31]+randArray[i-3]) % 4294967296
    randArray.append(gen)


def rand():
    """Returns a pseudo-random number"""
    global n
    randNum = (randArray[n]) # Pick from the pseudorandom sequence starting from n=344 as defined in docs
    randNum >>= 1
    n += 1  # Advance along pseudorandom sequence
    if n == MAX-1:
        n = 344  # If max, then wrap back around
    return randNum
