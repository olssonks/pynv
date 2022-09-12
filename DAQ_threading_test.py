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
        
        time.sleep(2)
        
        data = daq.AI_read()
        
        result = data.sum()
        
        daq.stop_task(daq.AI_task)
        
        cue.put(data)

    event.clear()

    return


def second(cue, event, figure, ax, plot1):
        
    #while not cue.empty():
    pop_data = cue.get(timeout = 5)
    print(pop_data.sum())
    update_plot(pop_data, figure, ax, plot1)
        
    
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
    print(data.shape)
    #plot1.set_xdata(x)
    d_mean = data.mean(axis=0)
    print(d_mean.shape)
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
    daq = DAQ('Dev1', SampleRate=25e3)
    daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE
    samps = 1024
    daq.prep_AI_channel(['ai0'], samps, num_chan = 1)
    
    cue = queue.Queue()
    event = threading.Event()
    
    fig, axs, plot1 = create_fig(samps)
    plt.show()
    
    m_thread = threading.Thread(target=main, 
                                args=(daq, cue, event,),
                                daemon=True
                                )
    
    m_thread.start()
    
    # s_thread = threading.Thread(target=second, 
    #                             args=(cue, event, fig, ax, plot1,),
    #                             daemon=True
    #                             )
    
    # s_thread.start()
    data_list = []
    while event.is_set() or not cue.empty():
        pop_data = cue.get(timeout = 5)
        data_list.append(pop_data)
        new_data = np.array(data_list)
        print(new_data)
        update_plot(new_data, fig, axs, plot1)
    
    plt.show(block=True)