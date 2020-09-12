for x in range(1, 8129):
    if x == sum([i if x % i is 0 else 0 for i in range(1, x)]):
        print(x)
