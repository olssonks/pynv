import numpy as np

from scipy.optimize import curve_fit

def lor(x, c, w, a, off):
    return 1 + off - (a/np.pi * w /( (x-c)**2 + (w)**2))

data = np.load('data/test_data.npy')
data = np.stack(data.reshape(2,10, 10000), axis=1)

dcut = 2
ucut = 9806

x1 = 2870 + data[0,1,dcut:ucut] * 200/2
y1 = data[0,0,dcut:ucut]

xfit = x1[1000:3000]
yfit = y1[1000:3000]


guesses = [2805, 5, 0.05, 0.01]

popt, pcov = curve_fit(lor, xfit, yfit, guesses, maxfev=10000)

f1 = lor(xfit, *popt)

# def main():
    
#     popt, pcov = curve_fit(lor, xfit, yfit, guesses, maxfev=10000)
    
#     f1 = lor(xfit, *popt)
    
#     return [xfit, yfit, f1]

# if __name__ == "__main__":
#    [xfit, yfit, f1] = main()