import numpy as np
from matplotlib.pyplot import plot, show

y = [29145, 33423, 39201, 43270, 48434, 53066, 57327, 62439, 67657, 73435, 79007, 84235, 88141,
     93806, 100042]

x = range(60)
difs = [y[i+1] - y[i] for i in range(len(y) - 1)]
coef = [difs[i] / y[i+1] for i in range(len(y) - 1)]

pred_poly_y = np.polyfit(range(len(y)), y, 3)
pred_val_y = np.polyval(pred_poly_y, x)

coef_poly = np.polyfit(range(len(coef))[-7:], coef[-7:], 1)

pred_y = y.copy()
for i in range(len(y), len(x)):
    pred_y.append(pred_y[-1]*(1+np.polyval(coef_poly, i)))
    #print(np.polyval(coef_poly, i))
print(len(pred_y))
#plot(x, pred_val_y, "blue")
plot(x[:len(y)], y, 'r*')
plot(x, pred_y, "orange")

show()