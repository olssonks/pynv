import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

def lor(x, c, w, a, off):
    return 1 + off - (a/np.pi * w /( (x-c)**2 + (w)**2))

def lor2(x, c1, w1, a1, c2, w2, a2, off):
    return 1 + off - (a1/np.pi * w1 /( (x-c1)**2 + (w1)**2)
                      + (a2/np.pi * w2 /( (x-c2)**2 + (w2)**2)))


# data = np.load('data/test_data.npy')
# data = np.stack(data.reshape(2, 10, 10000), axis=1)

# dcut = 2
# ucut = 9806

# xcut = 2870 + data[0,1,dcut:ucut] * 200/2
# ycut = data[0,0,dcut:ucut]

# x1 = xcut[1000:3000]
# x2 = xcut[8000:9300]
# y1 = ycut[1000:3000]
# y2 = ycut[8000:9300]

# xfit = [x1, x2]
# yfit = [y1/y1.max(), y2/y2.max()]

# guesses = [2805, 5, 0.05, 0.001]

# popt, pcov = curve_fit(lor, xfit[0], yfit[0], guesses, maxfev=10000)

# f1 = lor(xfit[0], *popt)

# guesses = [2950, 5, 0.05, 0.01]

# popt, pcov = curve_fit(lor, xfit[1], yfit[1], guesses, maxfev=10000)

# f2 = lor(xfit[1], *popt)

# fs = [f1, f2]

# guesses = [2805, 5, 0.05, 2950, 5, 0.05, 1e-2]

# x_two = np.concatenate( xfit )
# y_two = np.concatenate( yfit )

# popt, pcov = curve_fit(lor2, x_two, y_two, guesses, maxfev=10000)

# f_two = lor2(x_two, *popt)


x1 = np.linspace(2925, 2965, 1001)
y1 = lor(x1, 2945, 1, 0.25, 0) + lor(x1, 2945+3, 1, 0.15, 0) + lor(x1, 2945-3, 1, 0.15, 0)

xfit = [x1, 0]
yfit = [y1/y1.max(), 0]

guesses = [2940, 5, 0.05, 0.001]

popt, pcov = curve_fit(lor, xfit[0], yfit[0], guesses, maxfev=10000)

f1 = lor(xfit[0], *popt)

plt.plot(xfit[0], f1)
plt.plot(xfit[0], yfit[0])
plt.show()

def main():
    
    # data = np.load('data/test_data.npy')
    # data = np.stack(data.reshape(2,10, 10000), axis=1)
    
    x_full = np.linspace(2925, 2965, 1001)
    y_full = lor(x_full, 2945, 1, 0.25, 0) + lor(x_full, 2945+3, 1, 0.15, 0) + lor(x_full, 2945-3, 1, 0.15, 0)
    
    y_mid = lor(x_full, 2945, 1, 0.25, 0)
    
    x1 = np.array([np.linspace(2925, 2935, 200),
                     np.linspace(2942.5, 2947, 200),
                     np.linspace(2956.5, 2965, 200)
                     ]).flatten()
    y1 = lor(x1, 2945, 1, 0.25, 0) + lor(x1, 2945+3, 1, 0.15, 0) + lor(x1, 2945-3, 1, 0.15, 0)
    
    # dcut = 2
    # ucut = 9806
    
    # xcut = 2870 + data[0,1,dcut:ucut] * 200/2
    # ycut = data[0,0,dcut:ucut]
    
    # x1 = xcut[1000:3000]
    # x2 = xcut[8000:9300]
    # y1 = ycut[1000:3000]
    # y2 = ycut[8000:9300]
    
    # xfit = [x1/x1.max(), x2/x2.max()]
    # yfit = [y1/y1.max(), y2/y2.max()]
    
    xfit = [x1, 0]
    yfit = [y1/y1.max(), 0]
    
    guesses = [2940, 5, 0.05, 0.001]
    
    popt, pcov = curve_fit(lor, xfit[0], yfit[0], guesses, maxfev=10000)
    
    f1 = lor(x_full, *popt)
    
    # plt.plot(x_full, f1)
    # plt.plot(xfit[0], yfit[0])
    # plt.plot(x_full, y_full/y_full.max())
    # plt.plot(x_full, y_mid)
    
    plt.plot(x_full, np.gradient(f1)/np.gradient(f1).max())
    plt.plot(x_full, np.gradient(y_full)/np.gradient(y_full).max())
    plt.plot(x_full, np.gradient(y_mid)/np.gradient(y_mid).max())
    
    plt.xlim((2940, 2950))
    
    plt.show()

    
    # guesses = [2950, 5, 0.05, 0.01]
    
    # popt, pcov = curve_fit(lor, xfit[1], yfit[1], guesses, maxfev=10000)
    
    # f2 = lor(xfit[1], *popt)
    
    # fs = [f1, f2]
    
    ## Seperate fitting of each lorentzian faster than fitting both
    # guesses = [2805, 5, 0.05, 2950, 5, 0.05, 1e-2]
    
    # x_two = np.concatenate( xfit )
    # y_two = np.concatenate( yfit )
    
    # popt, pcov = curve_fit(lor2, x_two, y_two, guesses, maxfev=10000)
    
    # f_two = lor2(x_two, *popt)
    
    return

if __name__ == "__main__": 
    main()