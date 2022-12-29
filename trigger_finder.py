# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 19:37:00 2022

@author: walsworthlab
"""

import numpy as np
import matplotlib.pyplot as plt

def lor(x, c, w, a, off):
    return 1 + off - (a/np.pi * w /( (x-c)**2 + (w)**2))

center = 2945
span = 30

def freq_conv(volts, center, span):
    
    return center + volts * span/2

samps = 10001

volts = np.linspace(-0.98, 0.98, samps)

x1 = freq_conv(volts, center, span)
y1    = lor(x1, 2945, 0.5, 0.15, 0) + lor(x1, 2945+1.5, 0.5, 0.25, 0) + lor(x1, 2945+3, 0.5, 0.15, 0) + 0.01*np.random.random(samps)
ytrue = lor(x1, 2945, 0.5, 0.15, 0) + lor(x1, 2945+1.5, 0.5, 0.25, 0) + lor(x1, 2945+3, 0.5, 0.15, 0)

deriv = np.gradient(y1)


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

sm1 = np.gradient(smooth(y1, 100))

