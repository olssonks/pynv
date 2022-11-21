import pyvisa

class SG380:
    '''
    General Functions
        GetMWAmpl() in dBm
        GetMWFreq() in MHz
        GetMWStat()

        SetMWAmpl(power) in dBm
        SetMWFreq(freq) in MHz
        SetMWStat(bool) turns output on/off

        Close()

    SRS specific


        Reset()

    '''

    def __init__(self,
                 IPaddress = None,
                 port = '5025', ## SRS tcpip port number
                 configs = None
                ):
        ## create, open, and configure connection
        
        if not configs is None:
            self.set_configs(configs)
        
        else:
            rm = pyvisa.ResourceManager('@py')
            self.inst = rm.open_resource(
            				   'TCPIP0::'+IPaddress+'::'+port+'::SOCKET'
            					)
            self.inst.read_termination = '\r\n' ## specific termination for SRS
            
            self.frequency_units = 'MHz' ## default: work in MHz
            self.output_port = 'Currently Not Known: Check Current Frequency'
            
            self.current_Freq = self.GetMWFreq()
            self.current_Ampl = self.GetMWAmpl()
            self.current_Stat = self.GetMWStat()
        return
    
    def set_configs(self, configs):
        rm = pyvisa.ResourceManager('@py')
        IPaddress = configs['sig_gen']['IPs']
        self.inst = rm.open_resource(
        				   'TCPIP0::'+IPaddress+'::'+port+'::SOCKET'
        					)
        self.inst.read_termination = '\r\n' ## specific termination for SRS
        
        self.frequency_units = 'MHz' ## default: work in MHz
        self.output_port = 'Currently Not Known: Check Current Frequency'
        
        self.current_Freq = configs['measurement']['freqs'][0]
        self.current_Ampl = configs['measurement']['amps'][0]
        self.current_Stat = self.SetMWStat(1)
        return
    
    def GetID(self):
        msg = self.inst.query('*IDN?')
        return msg


    def GetMWAmpl(self):
        if float(self.current_Freq) < 1: ## 1 MHz
            prefix = 'AMPL'
        else:
            prefix = 'AMPR'
        reading = self.inst.query(prefix+'?')
        ## above returns string ending with 'dBm'
        ## ex: '-1.1dBm'
        self.current_Ampl = float(reading[:-3]) ## cut dBm from string
        return self.current_Ampl


    def GetMWFreq(self):
        suffix = self.frequency_units
        reading = self.inst.query('FREQ? ' + suffix)
        self.current_Freq = float(reading)
        
        if (self.current_Freq \
            * frequency_units[self.frequency_units]) < 950e3:
            self.output_port = 'BNC'
        else:
            self.output_port = 'N-Type'
        
        return self.current_Freq


    def GetMWStat(self):
        if float(self.current_Freq) < 1: ## 1 MHz
            prefix = 'ENBL'
        else:
            prefix = 'ENBR'
        reading = self.inst.query(prefix+'?')
        self.current_Stat = int(reading)
        return self.current_Stat


    def SetMWAmpl(self, value):
        if float(self.current_Freq) < 1: ## 1 MHz
            prefix = 'AMPL'
        else:
            prefix = 'AMPR'
        suffix = '' ## no suffix needed
        msg = prefix+str(value)+suffix
        self.inst.write(msg)
        self.current_Ampl = value
        return


    def SetMWFreq(self, value):
        prefix = 'FREQ '
        suffix = ' ' + self.frequency_units
        msg = prefix+str(value)+suffix
        self.inst.write(msg)
        self.current_Freq = value
        return


    def SetMWStat(self, value):
        ## 0 or 1 for off or on
        if float(self.current_Freq) < 1: ## 1 MHz
            prefix = 'ENBL'
        else:
            prefix = 'ENBR'
        suffix = ''
        msg = prefix+str(value)+suffix
        self.inst.write(msg)
        self.current_Stat = value
        return


    def SetMWSweep(self, center, span, rate):
        ## rate in Hz
        cntr = center * frequency_units[self.frequency_units]
        dev = span/2 * frequency_units[self.frequency_units]
        
        bands = [band * 1e6 for band in \
                 Sweep_bands[self.get_freq_sweep_range(cntr)]
                ]
        
        if (cntr-dev) < bands[0] or (cntr+dev)> bands[1]:
            print('Scan out of range: reduce span or shift center')
        else:
            self.inst.write('MODL 1')
            self.inst.write('TYPE 3') ## 3 for sweep
            self.SetMWFreq(center)
            self.inst.write(f'SDEV {dev} Hz')
            self.inst.write(f'SRAT {rate} Hz')
            self.inst.write('SFNC 1') ## 1 for ramp
        return

    def SetMod(self, state):
        ## 0/1 for off/on
        self.inst.write(f'MODL {state}')
        return


    def Reset(self):
        reading = self.inst.write('*RST')
        return reading
    

    def get_freq_sweep_range(self, center):
        cntr = center/ 1e6 ## convert to MHz
        idx = 0
        for band in Sweep_bands:
            if  cntr < band[1]:
                break
            else:
                idx += 1
        
        return idx
        
### Utility Definitons ###

## SG382 and SG384 frequency sweep bands in MHz
Sweep_bands = [(0,64), 
               (60, 128), 
               (119, 256),
               (238, 512), 
               (476, 1024), 
               (951, 2048),
               (1901, 4099), 
               (3801, 8199)
               ] 

frequency_units = {'Hz' : 1,
                   'kHz': 1e3,
                   'MHz': 1e6,
                   'GHz': 1e9
                   }