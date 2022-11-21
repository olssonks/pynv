from srs import SG380

from nidaq import DAQ

import numpy as np

import PyDAQmx

sg = SG380('10.229.42.141')

sg.SetMWFreq(2870)
sg.SetMWAmpl(0.0)
sg.SetMWStat(1)

sg.SetMWSweep(2870, 250, 10)

daq = DAQ('dev1', SampleRate=100e3)
daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE

samps = 100000

x_vals = np.arange(samps)

y_vals = np.zeros(samps)

daq.prep_AI_channel(['ai23','ai1'], samps, num_chan = 2)

daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.88)

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

# center = 10e-6
# span = 5e-6
# rate = 10

# def VoltToFreq(volts, center, span):
#     freqs = center + np.array(volts)*span/2
#     return freqs