import queue
import threading

from srs import SG380
from nidaq import DAQ
from utils.data_logger import Logger

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


def second(cue, event, logger, genre, info):
    data = cue.get(timeout = 5)
    print(data.shape)
    logger.log_data(data, genre, info=info)
    return

def create_fig(samps):
    figure, axs = plt.subplots(2,1, figsize=(4,5))
    # Data Coordinates
    x = np.arange(samps)
    y = np.zeros(samps)
    # GUI
    plt.ion()
    #  Plot
    plot1, = axs[0].plot(x, y)
    # Labels
    axs[0].set_xlabel("X-Axis",fontsize=18)
    axs[0].set_ylabel("Y-Axis",fontsize=18)
    return figure, axs, plot1


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

if __name__ == "__main__":
    
    file_name = time.strftime("%Y%m%d") + '_QDM.h5'

    m_type = 'ODMR'
    data_genres = ['raw']
    configs = {'sweep_center': 2870,
               'sweep_span': 250,
               'sweep_rate': 10}

    record = Logger(file_name, config= configs)
    record.set_meas_type(m_type)

    info = {'units': ['MHz','mV']}
    
    sg = SG380('10.229.42.141')
    sg.SetMWFreq(2870)
    sg.SetMWAmpl(0.0)
    sg.SetMWStat(1)
    sg.SetMWSweep(2870, 250, 10)
    
    samps = 10000
    daq = DAQ('Dev2', SampleRate=100e3)
    daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE
    daq.prep_AI_channel(['ai1'], samps, num_chan = 1)
    daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.88)

    
    cue_acq = queue.Queue()
    event = threading.Event()
    
    fig, axs, plot1 = create_fig(samps)
    plt.show()
    
    m_thread = threading.Thread(target=main, 
                                args=(daq, cue_acq, event,),
                                daemon=True
                                )
    m_thread.start()
    
    cue_rec = queue.Queue()
    #event = threading.Event()
    
    # s_thread = threading.Thread(target=second, 
    #                             args=(cue_rec, event, record, data_genres[0], info,),
    #                             daemon=True
    #                             )
    

    # s_thread.start()
    
    data_list = []
    while event.is_set() or not cue_acq.empty():
        pop_data = cue_acq.get(timeout = 5)
        record.log_data(pop_data, data_genres[0], info=info)
        #cue_rec.put(pop_data)
        data_list.append(pop_data)
        new_data = np.array(data_list)
        
        avg_data = new_data.mean(axis = 0)
        
        fit_data(data, configs)
        
        update_plot(new_data, fig, axs, plot1)
    
    #record.log_data(new_data, data_genres[0], info=info)
    record.h5file.flush()
    record.h5file.close()
    
    plt.show(block=True)
    