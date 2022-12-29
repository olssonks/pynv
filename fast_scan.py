import queue
import threading
import time

## Instrument Control (DAQ and Signal Generator)
from srs import SG380
from nidaq import DAQ
import PyDAQmx
import time

## Utilities
from utils.Args import get_configs
from utils.data_logger import Logger
from utils.simple_plots import update_plot, fast_scan_fig

import numpy as np
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
    
    configs = get_configs()
    
    file_name = time.strftime("%Y%m%d") + '_QDM.h5'

    m_type = configs['measurement']['type']
    data_genres = configs['data']['genres'][0]
    info = configs['data']

    record = Logger(file_name, configs=configs)
    record.set_meas_type(m_type)

    ## Set up signal generator
    IP = configs['sig_gen']['IPs'][0]
    sg = SG380(IPaddress=IP)
    sweep = configs['measurement']['sweep']
    sg.SetMWSweep(sweep['center'], 
                  sweep['span'], 
                  sweep['rate']
                  )
    sg.SetMWStat(1)
    
    ## Set up DAQ
    samps = configs['daq']['analog_input']['ai_samples']
    channels = configs['daq']['analog_input']['ai_channels']
    num_chan = len(channels)
    
    #daq = DAQ(configs=configs)
    daq = DAQ(DeviceName=configs['daq']['daq_device'], 
              SampleRate=100e3)
    daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE
    
    # daq.prep_AI_channel(channels, 
    #                     samps, 
    #                     num_chan = num_chan
    #                     )
    
    # daq.prep_Analog_trigger(daq.AI_task, 
    #                         'APFI0', 
    #                         level=-0.88)
    
    daq = DAQ('dev1', SampleRate=100e3)
    daq.exp_params['terminal_type'] = PyDAQmx.DAQmx_Val_RSE

    samps = 10000

    daq.prep_AI_channel(['ai23'], samps, num_chan = 1)

    daq.prep_Analog_trigger(daq.AI_task, 'APFI0', level=-0.88)

    
    cue_acq = queue.Queue()
    event = threading.Event()
    
    fig, axs, plot1 = fast_scan_fig(samps, configs)
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
        record.log_data(pop_data, data_genres, info=info)
        #cue_rec.put(pop_data)
        data_list.append(pop_data)
        new_data = np.array(data_list)
        
        avg_data = new_data.mean(axis = 0)
        
        ## find camera trigger points
        #fit_data(data, configs)  ## fit probably not necessary, use max/min of derivated
        
        update_plot(new_data, fig, axs, plot1)
    
    #record.log_data(new_data, data_genres[0], info=info)
    record.h5file.flush()
    record.h5file.close()
    
    sg.SetMWStat(0)
    
    plt.show(block=True)
    
    