from srs import SG380

from nidaq import DAQ

import numpy as np
import matplotlib.pyplot as plt

import PyDAQmx

# sg = SG380('10.229.42.141')

# sg.SetMWFreq(2870)
# sg.SetMWAmpl(0.0)
# sg.SetMWStat(1)

# sg.SetMWSweep(2870, 250, 10)

daq = DAQ('Dev2', SampleRate=10e3, VoltageLims=2.0)
daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_Diff

samps = 10000

x_vals = np.arange(samps)

y_vals = np.zeros(samps)

daq.prep_AI_channel(['ai1', 'ai23'], samps, num_chan = 2)

daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.90)

daq.start_task( daq.AI_task )

data = daq.AI_read()

daq.stop_task(daq.AI_task)

# daq.start_task( daq.AI_task )

# data2 = daq.AI_read()

# daq.stop_task(daq.AI_task)

# #daq.clear_task(daq.AI_task)

# from datetime import datetime
# from matplotlib import pyplot
# from matplotlib.animation import FuncAnimation
# from random import randrange

# #x_data, y_data = [], []

# figure = pyplot.figure()
# line, = pyplot.plot(x_vals, y_vals, '-')

# def update(frame):
#     daq.start_task( daq.AI_task )

#     data = daq.AI_read()

#     daq.stop_task(daq.AI_task)
    
#     y_vals = np.array(data[:1000])
#     line.set_data(x_vals, y_vals)
#     figure.gca().relim()
#     figure.gca().autoscale_view()
#     return line,

# animation = FuncAnimation(figure, update, interval=20)

# pyplot.show()

center = 2870
span = 200
rate = 1

def VoltToFreq(volts, center, span):
    freqs = center + np.array(volts)*span/2
    return freqs

#######################
### Single Run Analysis
#######################

def convert_data(data):
    trim = 100
    data_r = data.reshape(2, samps)
    x = VoltToFreq(data_r[0], center, span)
    y = data_r[1]
    
    y[:trim] = y[trim]
    return x,y

x0, y0 = convert_data(data)
    