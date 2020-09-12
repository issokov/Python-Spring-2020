from itertools import product
for s, e, v, n, i, x, w, y in product(range(10), repeat=8):
    if s != 0 and len({s, e, v, n, i, x, w, y}) == 8:
        if 2*(10050*s + 1000*e + 100*v + 10*e + n)\
           - 100010 - w*10000 - e*1000 - 100*n - y == -i*10 -x:
            print(s, e, v, e, n, ' + ', s, e, v, e, n, ' + ', s, i, x, ' = ',
                  1, w, e, n, 1, y, sep='')
            break
