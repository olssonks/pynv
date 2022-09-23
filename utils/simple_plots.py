import queue
import threading

from srs import SG380
from nidaq import DAQ
from utils.data_logger import Logger
from utils.Args import get_configs

import numpy as np
import PyDAQmx
import time


import matplotlib.pyplot as plt

def update_plot(data, figure, axs, plot1):
    #plot1.set_xdata(x)
    d_mean = data.mean(axis=0)
    axs[0].set_ylim(d_mean.min(), d_mean.max())
    plot1.set_ydata(d_mean)
    
    #x = np.arange(data[-1].size)
    
    for d in data:
        x = np.arange(d.size)
        axs[1].plot(x, d)
        #axs[1].set_ylim( data[-1].min(),  data[-1].max())
    
    figure.canvas.draw()
    figure.canvas.flush_events()
    plt.pause(0.1)
    return

def fast_scan_fig(samps, config):
    
    if configs['data']['info']:
        x_label, y_label = config['data']['info']['units']
    else: 
        x_label, y_label = ('X Axis', 'Y-Axis')
    
    figure, axs = plt.subplots(2,1, figsize=(4,5))
    # Data Coordinates
    x = np.arange(samps)
    y = np.zeros(samps)
    # GUI
    plt.ion()
    #  Plot
    plot1, = axs[0].plot(x, y)
    # Labels
    axs[0].set_xlabel(x_label,fontsize=18)
    axs[0].set_ylabel(y_lable,fontsize=18)
    return figure, axs, plot1