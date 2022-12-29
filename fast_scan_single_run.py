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

samps = 10000

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
    trim = 200 ## remove points where freq scan is resetting
    window = 10
    data_r = data.reshape(2, samps)
    x = VoltToFreq(data_r[0], center, span)
    y = data_r[1]
    
    x = x[10:-trim]
    y = smooth(y, window)
    y = y[10:-trim]
    return x, y, data_r[0], data_r[1]

def calc_trig(pl_data):
## max gradient points
    grad = np.gradient(pl_data)
    lr1, lr2 = grad[:int(samps/2)].argmin(), grad[:int(samps/2)].argmax()
    
    ur1, ur2 = grad[int(samps/2):].argmin()+ int(samps/2), grad[int(samps/2):].argmax() + int(samps/2)
    
    triggers = np.zeros(pl_data.shape[0])
    
    trig_span = 2
    triggers[lr1 - trig_span:lr1 + trig_span] = 1
    triggers[lr2 - trig_span:lr2 + trig_span] = 1
    triggers[ur1 - trig_span:ur1 + trig_span] = 1
    triggers[ur2 - trig_span:ur2 + trig_span] = 1
    
    return triggers


def main():
    daq = DAQ('Dev2', SampleRate=100e3, VoltageLims=10.0)
    daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_Diff
    
    
    
    
    daq.prep_AI_channel(['ai1', 'ai23'], samps, num_chan = 2)
    
    daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.90)
    
    
    
    x_set = []
    y_set = []
    x_raw_set = []
    y_raw_set = []
    trig_set = []
    for i in range(10):
        daq.start_task( daq.AI_task )
        
        data = daq.AI_read()
        
        x, y, x_raw, y_raw = convert_data(data)
        
        trig = calc_trig(y)
        
        x_set.append(x)
        y_set.append(y)
        x_raw_set.append(x_raw)
        y_raw_set.append(y_raw)
        trig_set.append(trig)
        
        daq.stop_task(daq.AI_task)
        
    return x_raw_set, y_raw_set, x_set, y_set, trig_set
        
    






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




    
    