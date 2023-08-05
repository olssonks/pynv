import queue
import threading

from nidaq import DAQ

import numpy as np
import PyDAQmx
import time


import matplotlib.pyplot as plt

def main(daq, cue, event):
    
    event.set()
    for i in range(10):
    
        daq.start_task( daq.AI_task )
        
        data = daq.AI_read()
        
        daq.stop_task(daq.AI_task)
        
        cue.put(data)

    event.clear()

    return

if __name__ == "__main__":
    
    samps = 10000
    daq = DAQ('Dev2', SampleRate=100e3)
    daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE
    daq.exp_params['time_source'] = 'PFIO'
    daq.prep_AI_channel(['ai1'], samps, num_chan = 1)
    daq.prep_Digital_trigger(daq.AI_task, 'PFI0')

    
    cue_acq = queue.Queue()
    event = threading.Event()
    
    
    m_thread = threading.Thread(target=main, 
                                args=(daq, cue_acq, event,),
                                daemon=True
                                )
    m_thread.start()
    
    