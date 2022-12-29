import PyDAQmx
import numpy as np
import time

class DAQ:
    """
    NiDAQ communication class based on PyDAQmx module:
        https://pythonhosted.org/PyDAQmx/
        Mimics MATLAB/C type functions/commands, where
        'PyDAQmx' replaces 'daq.ni.NIDAQmx' from MATLAB

        PyDAQmx is different than National Instruments own
        Python module: nidaqmx-python

    Args:
        - `DeviceName` (str): Name of DAQ device (e.g. 'Dev1')
        - `SampleRate` (float): Sample Rate of DAQ. Depends on model
            and can be set to an arb. rate up to the maximum.
        - `VoltageLims` (float): Absolute value of the maximum and
            minimum voltage measured on the analog input channels.


    DAQmx needs specific C data types, which are converted through `byref`.
    """

    def __init__(self,
                 DeviceName='',
                 SampleRate=1e6,
                 VoltageLims=1.0,
                 configs = None
                 ):
        ## Possibe Lims: ±0.1 V, ±0.2 V, ±0.5 V, ±1 V, ±2 V, ±5 V, ±10 V
        
        if not configs is None:
            self.set_configs(configs)
        else:
            self.device_name = DeviceName
            ## Parameters: default values used here are for USB 6363
            self.sample_rate = SampleRate
    
        self.AI_task = 0
        self.AI_read_size = 0 ## size in samples
        self.AI_channels = 1
        self.AI_data = None

        self.AO_task = 0
        self.AO_write_size = 0 ## size in samples

        ## dictionary of parameters for the experiment
        ## default values here can be changed per experiment
        self.exp_params = {'voltage_limits': VoltageLims,
                           'terminal_type': PyDAQmx.DAQmx_Val_Diff,
                           'units': PyDAQmx.DAQmx_Val_Volts,
                           'fill_mode': PyDAQmx.DAQmx_Val_GroupByChannel,
                           'timeout': PyDAQmx.DAQmx_Val_WaitInfinitely,
                           'time_source': 'OnboardClock',
                           'active_edge': PyDAQmx.DAQmx_Val_Rising,
                           'sample_mode': PyDAQmx.DAQmx_Val_FiniteSamps,
                           'output_voltage_limits': VoltageLims,
                           'output_rate': 1e3, ## Output not same a input rate
                           'output_time_source': 'OnboardClock'
                           }
        return
        
    def set_configs(self, configs):
        self.device_name = configs['daq']['daq_device']
        self.sample_rate = configs['daq']['ai_sample_rate']
        return

    def prep_AI_channel(self, read_channels_list, SampsToRead, num_chan = 1):

        task = PyDAQmx.Task() # 'ai_task-'+f'{(time.time() % 1):.8f}'[2:]
        self.AI_read_size = SampsToRead
        self.AI_channels = num_chan
        
        if not num_chan == 1:
            chan = ''
            for ch in read_channels_list:
                chan = chan + '/' + self.device_name \
                + '/' + ch + ','
        else: 
            chan = '/' + self.device_name + '/' + read_channels_list[0]

        ## Create Analog Input Channel
        task.CreateAIVoltageChan(chan,
                                 '',
                                 self.exp_params['terminal_type'],
                                 -self.exp_params['voltage_limits'],
                                 self.exp_params['voltage_limits'],
                                 self.exp_params['units'],
                                 None
                                 )

        time_source = str(self.exp_params['time_source'])
        
        if time_source.find('PFI') >= 0:
            ## Configure channel clock to external channel
            task.CfgSampClkTiming('/' + self.device_name
                                  + '/' + time_source.upper(),
                                  self.sample_rate,
                                  self.exp_params['active_edge'],
                                  self.exp_params['sample_mode'],
                                  int(SampsToRead)
                                  )
            print(f'Using Channel {time_source} as time source')
        else:
            ## Configure channel internal clock
            task.CfgSampClkTiming(time_source,
                                  self.sample_rate,
                                  self.exp_params['active_edge'],
                                  self.exp_params['sample_mode'],
                                  int(SampsToRead)
                                  )
            print(f'Channel {read_channels_list}: Using Onboard time source')

        self.AI_task = task
        return
    ## end `prep_AI_read_task`


    def AI_read(self):
        
        SampsToRead = self.AI_read_size
        
        # if self.AI_data is not None:
        #     data = np.zeros(int((SampsToRead*self.AI_channels,)), dtype=np.float64)
        
        data = np.zeros(int(SampsToRead*self.AI_channels), dtype=np.float64)
        
        self.AI_task.ReadAnalogF64(SampsToRead,
                               PyDAQmx.float64(self.exp_params['timeout']),
                               self.exp_params['fill_mode'],
                               data,
                               int(SampsToRead*self.AI_channels),
                               PyDAQmx.byref(PyDAQmx.int32()),
                               None
                               )
        
        return data
    ## end `read`
    

    def prep_AO_channel(self, write_channels_list, SampsToWrite, num_chan):
        
        task = PyDAQmx.Task() #'ao_task-'+f'{(time.time() % 1):.8f}'[2:]
        
        self.AO_write_size = SampsToWrite
        
        self.AO_channels = num_chan
        
        if not num_chan == 1:
            chan = ''
            for ch in write_channels_list:
                chan = chan + '/' + self.device_name \
                + '/' + ch + ','
        else: 
            chan = '/' + self.device_name + '/' + write_channels_list[0]

        task.CreateAOVoltageChan(chan,
                                 '',
                                 -self.exp_params['output_voltage_limits'],
                                 self.exp_params['output_voltage_limits'],
                                 self.exp_params['units'],
                                 None
                                 )
        time_source = self.exp_params['output_time_source']
        if time_source.find('PFI') > 0:
            ## Configure channel clock to external channel
            task.CfgSampClkTiming('/' + self.device_name
                                  + '/' + time_source.upper(),
                                  self.exp_params['output_rate'],
                                  self.exp_params['active_edge'],
                                  self.exp_params['sample_mode'],
                                  int(SampsToWrite)
                                  )
            print(f'Using Channel {time_source} as time source')
        else:
            ## Configure channel internal clock
            task.CfgSampClkTiming(time_source,
                                  self.exp_params['output_rate'],
                                  self.exp_params['active_edge'],
                                  self.exp_params['sample_mode'],
                                  int(SampsToWrite)
                                  )
            print('Using OnBoard as time source')

        self.AO_task = task
        return
    
    
    def AO_write(self, write_Array):
        
        write_per_chan = int(write_Array.shape[0] / self.AO_channels)
        
        #if len(write_Array) == self.AO_write_size:
        self.AO_task.WriteAnalogF64(write_per_chan,
                                    0, ## auto start off
                                    self.exp_params['timeout'],
                                    self.exp_params['fill_mode'],
                                    write_Array,
                                    PyDAQmx.byref(PyDAQmx.int32()),
                                    None
                                    )
        # else:
        #     print('Write array length not equal to length prepared for AO')
        
        return


    def prep_Analog_trigger(self, task, 
                            trig_channel, 
                            slope = PyDAQmx.DAQmx_Val_FallingSlope,
                            level = -0.9):
        
        if trig_channel[:4] == 'APFI':
            chan_name = trig_channel
        else:
           chan_name = self.device_name + '/' + trig_channel
                                      
        task.CfgAnlgEdgeStartTrig(chan_name,
                                  slope,
                                  level)
        
        return
    ## end `Analog_trigger`
    
    
    def prep_Digital_trigger(self, task, 
                            trig_channel, 
                            slope = PyDAQmx.DAQmx_Val_RisingSlope,):
        
        if trig_channel[:3] == 'PFI':
            chan_name = trig_channel
        else:
           chan_name = self.device_name + '/' + trig_channel
                                      
        task.CfgDigEdgeStartTrig(chan_name, slope)
        
        return
    ## end `Analog_trigger`
    

    def start_task(self, task):
        task.StartTask()
        return
    ## end `start`

    def stop_task(self, task):
        task.StopTask()
        return
    ## end `stop`

    def clear_task(self, task):
        task.ClearTask()
        return
    ## end `clear`
    
    
    def get_exp_params(self):
        print('Current Experimental Parameters')
        
        for key, value in self.exp_params.items():
            
            if key in ['voltage_limits',
                       'output_voltage_limits',
                       'output_rate']:
                ## any parameter that can possibly by 0 or 1, put in list here
                code = value
            elif value in PyDAQmx_int_values.keys():
                code = PyDAQmx_int_values[value]
            else:
                code = value
            
            print(f'{key} : {code}')
        return
    
    
    def get_param_options(self):
        
        for key in param_options.keys():
            print(key)
            for param in param_options[key]:
                print("---", param)
                
        return


"""
End of Class

Possible Additions/Issues to address:

    -`prep_trig_acq`: May want to move all channel creation/config to
        initializaiton, function could just be for stopping/starting
        looking for triggers

    - Multiple analog input channels
        - could be list in arguments

    - Multliple trigger inputs
        - could be list in arguments
        - start trigger and read trigger
        - multiple different read triggers?
            When would this be the case?

    - Analog outputs
        - Will need to set this up if Python and MATLAB can't
            talk to the DAQ at the same time.
"""
PyDAQmx_int_values = {10106: 'PyDAQmx.DAQmx_Val_Diff',
                      10083: 'PyDAQmx.DAQmx_Val_RSE',
                      10078: 'PyDAQmx.DAQmx_Val_NRSE',
                      10348: 'PyDAQmx.DAQmx_Val_NRSE',
                      0: 'PyDAQmx.DAQmx_Val_GroupByChannel',
                      1: 'PyDAQmx.DAQmx_Val_GroupByScanNumber',
                      -1.0: 'PyDAQmx.DAQmx_Val_WaitInfinitely',
                      10280: 'PyDAQmx.DAQmx_Val_Rising',
                      10171: 'PyDAQmx.DAQmx_Val_Falling',
                      10178: 'PyDAQmx.DAQmx_Val_FiniteSamps',
                      10123: 'PyDAQmx.DAQmx_Val_ContSamps',
                      12522: 'PyDAQmx.DAQmx_Val_HWTimedSinglePoint'
                      }


param_options = {'voltage_limits': ['0.1', '0.2', '0.5',
                                    '1', '2', '5', '10'],
                   'terminal_type': ['PyDAQmx.DAQmx_Val_Diff', 
                                     'PyDAQmx.DAQmx_Val_RSE', 
                                     'PyDAQmx.DAQmx_Val_NRSE'],
                   'units': 'PyDAQmx.DAQmx_Val_Volts',
                   'fill_mode': ['PyDAQmx.DAQmx_Val_GroupByChannel',
                                 'PyDAQmx.DAQmx_Val_GroupByScanNumber'],
                   'timeout': ['PyDAQmx.DAQmx_Val_WaitInfinitely',
                               'Time in Seconds'],
                   'time_source': ['OnboardClock',
                                   'Clock Channel'],
                   'active_edge': ['PyDAQmx.DAQmx_Val_Rising',
                                   'PyDAQmx.DAQmx_Val_Falling'],
                   'sample_mode': ['PyDAQmx.DAQmx_Val_FiniteSamps',
                                   'PyDAQmx.DAQmx_Val_ContSamps',
                                   'PyDAQmx.DAQmx_Val_HWTimedSinglePoint'],
                   'output_voltage_limits': ['0.1', '0.2', '0.5',
                                             '1', '2', '5', '10'],
                   'output_rate': "User Defined in Hz",
                   'output_time_source':  ['PyDAQmx.DAQmx_Val_OnboardClock',
                                           'Clock Channel']
                   }