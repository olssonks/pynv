from srs import SG380

from nidaq import DAQ

import numpy as np
import matplotlib.pyplot as plt
import time

import PyDAQmx

# sg = SG380('10.229.42.141')

# sg.SetMWFreq(2870)
# sg.SetMWAmpl(0.0)
# sg.SetMWStat(1)

# sg.SetMWSweep(2870, 250, 10)

daq = DAQ('Dev2', SampleRate=10e3, VoltageLims=10.0)
daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_Diff

daq3 = DAQ('Dev3', SampleRate=10e3, VoltageLims=10.0)
daq3.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE

samps = 10000



daq.prep_AI_channel(['ai1', 'ai23'], samps, num_chan = 2)

daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.90)

daq3.prep_AI_channel(['ai1'], samps, num_chan = 1)

daq3.prep_Digital_trigger(daq3.AI_task, 'PFI0')



daq.start_task( daq.AI_task )

data = daq.AI_read()

daq.stop_task(daq.AI_task)

x_vals = np.arange(samps)

y_vals = np.zeros(samps)

center = 2870
span = 200
rate = 1

def VoltToFreq(volts, center, span):
    freqs = center + np.array(volts)*span/2
    return freqs

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

#######################
### Single Run Analysis
#######################

def convert_data(data):
    trim = 100
    window = 10
    data_r = data.reshape(2, samps)
    x = VoltToFreq(data_r[0], center, span)
    y = data_r[1]
    
    x = x[trim:-trim]
    y = smooth(y, window)
    y = y[trim:-trim]
    #y = smooth(y, trim)
    return x,y

x0, y0 = convert_data(data)


## max gradient points
grad = np.gradient(y0)
lr1, lr2 = grad[:int(samps/2)].argmin(), grad[:int(samps/2)].argmax()

ur1, ur2 = grad[int(samps/2):].argmin()+ int(samps/2), grad[int(samps/2):].argmax() + int(samps/2)

triggers = np.zeros(samps)

trig_span = 2
triggers[lr1 - trig_span:lr1 + trig_span] = 1
triggers[lr2 - trig_span:lr2 + trig_span] = 1
triggers[ur1 - trig_span:ur1 + trig_span] = 1
triggers[ur2 - trig_span:ur2 + trig_span] = 1

write_array = np.zeros(samps)
write_array[int(samps/4):int(samps/2)] = 1
write_array[int(samps/2):] = 2

write_array = np.append(write_array, 5.0 * np.ones(samps))



#daq.prep_AI_channel(['ai3'], samps, num_chan = 1)
#daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.90)
#daq.start_task( daq.AI_task )

daq.prep_AO_channel(['ao3', 'ao2'], samps, num_chan=2)
daq.prep_Analog_trigger(daq.AO_task, 'APFI1', level=-0.90)

#daq3.start_task(daq3.AI_task)

daq3.start_task(daq3.AI_task)

daq.AO_write(write_array)

daq.start_task( daq.AO_task )




data3 = daq3.AI_read()

time.sleep(5)

daq3.stop_task( daq3.AI_task )
daq.stop_task( daq.AO_task )




####
## Alternate filter
####
def simple_exp_smooth(d,extra_periods=1,alpha=0.4):  
  d = np.array(d)  # Transform the input into a numpy array    
  cols = len(d)  # Historical period length    
  d = np.append(d,[np.nan]*extra_periods)  # Append np.nan into the demand array to cover future periods    
  f = np.full(cols+extra_periods,np.nan)  # Forecast array    
  f[1] = d[0]  # initialization of first forecast    
  # Create all the t+1 forecasts until end of historical period    
  for t in range(2,cols+1):      
      f[t] = alpha*d[t-1]+(1-alpha)*f[t-1]  
  f[cols+1:] = f[t]  # Forecast for all extra periods  
  return f




    
    