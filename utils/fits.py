import numpy as np

from scipy.optimize import curve_fit

def fit(model, x, y, guesses=False):
    
    if not guesses:
        popt, pcov = curve_fit(model, x, y, guesses, maxfev=10000)
    else:
        popt, pcov = curve_fit(model, x, y, maxfev=10000)
    
    return popt, pcov

## Models

def Lorentzian(x, center, width, amplitude, offset):
    return 1 + offset - (amplitude/np.pi 
                         * width /( (x-center)**2 + (width)**2))
