import math

a = int(input("Please input the start number: "))
b = int(input("Please input the end number: "))


def find(x):
    if x <= 1:
        return 0
    y = math.floor(math.sqrt(x))
    for i in range(2, y+1):
        if x % i == 0:
            return 0
    return 1


def find_prime(start: int, end: int):
    list = []
    for i in range(start, end+1):
        if find(i):
            list.append(i)
    print(list)
    return list


find_prime(a, b)
