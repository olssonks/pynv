# Kevin Olsson
# Last updated: Sep 12 2022

import numpy as np
import tables
import time

from measurement_types import measurement_types, types_data


class Logger:

    def __init__(self,
                 file_name,
                 configs={}, 
                 compress=False):
        # default compression settings
        self.compress = compress
        self.complevel = 9
        self.complib = 'blosc'
        self.shuffle = True
        self.bitshuffle = True

        self.file_name = file_name
        self.h5file = self.get_file(self.file_name)
        self.meas_type = ''
        self.meas_num = 0
        self.meas_config = configs

        

        self.expectedrows = 128
        self.atom = tables.Atom.from_sctype('float64')
        #self.chunkshape = (128,2,256)

        self.current_arrays = {}

        return


    def get_file(self, name):
        
        if self.compress:
            filt = tables.Filters(complevel=self.complevel,
                                  complib=self.complib,
                                  shuffle = self.shuffle,
                                  bitshuffle=self.bitshuffle)
        else:
            filt = None

        if not '.h5' == name[-3:]:
            name = name + '.h5'

        file = tables.open_file(name, mode='a', filters=filt)
        return file


    def set_meas_type(self, m_type):
        '''Check name for type of measurement'''
        if m_type in measurement_types:
            self.meas_type = m_type
        else:
            print('Type not listed, using type = OTHER')
            self.meas_type = 'OTHER'
        self.data_location = self.set_loc(self.meas_config)
        return


    def set_loc(self, meas_config):
        '''
        Gets type of measurement from file name, then checks/makes group for
        this type of measurement. Creates group for the nth measurement of this 
        type, with 0 indexing, and saves the configurate as an attribute.
        Example: New Rabi measurement
        location: '/Rabi/M000'
        Example: 5th ODMR measurment
        location: '/ODMR/M004'

        '''
        m_type = self.meas_type

        if (self.h5file.__contains__('/' + m_type)
                and len(dict(self.h5file.root
                             ['/' + m_type +
                              f'/M{self.meas_num:03d}']
                             ._v_children
                             ))
            ):

            self.meas_type = m_type
            meas = self.h5file.root['/' + m_type]
            self.meas_num = len(dict(meas._v_children).keys())
            loc = self.h5file.create_group(meas,
                                           f'M{self.meas_num:03d}')
            self.h5file.set_node_attr(loc, 'config', str(meas_config))
            self.meas_type = m_type
            self.meas_num = self.meas_num + 1
        else:
            if not self.h5file.__contains__('/' + m_type):
                meas = self.h5file.create_group(self.h5file.root, m_type)

                loc = self.h5file.create_group(meas, f'M{self.meas_num:03d}')
            else:
                loc = self.h5file.root['/' + m_type+ f'/M{self.meas_num:03d}']

            self.h5file.set_node_attr(loc, 'config', str(meas_config))
            self.meas_type = m_type
            self.meas_num = 1

        self.h5file.flush()
        return loc


    def log_data(self, data, genre, info=''):

        if not self.h5file.__contains__(self.data_location._v_pathname
                                        + f'/{genre}'):
            dshape = list(data.shape)
            array_shape = [0]
            array_shape.extend(dshape)
            self.current_arrays[f'{genre}'] = self.h5file.create_earray(
                self.data_location,
                f'{genre}',
                atom=self.atom,
                shape=array_shape,
                expectedrows=self.expectedrows
            )

        self.current_arrays[f'{genre}'].append([data])

        if len(info):
            self.h5file.set_node_attr(self.current_arrays[f'{genre}'],
                                      'info',
                                      str(info))
        
        self.h5file.set_node_attr(self.current_arrays[f'{genre}'],
                                  'time',
                                  time.time_ns() )
        self.h5file.flush()
        return


    # def block(self, number):
    #     ## return block represetation of number (i.e. in powers of 2)
    #     ## [0, 3, 4, 7] = 2^0 + 2^3 + 2^4 + 2^7 = 153
    #     ## used to determine chunksize

    #     v = []

    #     # Converting the decimal number
    #     # into its binary equivalent.
    #     print ("Blocks for %d : " %x, end="")
    #     while (x > 0):
    #         v.append(int(x % 2))
    #         x = int(x / 2)

    #     return


# End of Class


class Reader:

    def __init__(self, file_name):
        self.file_name = file_name
        self.h5file = tables.open_file(file_name, 'r')
        self.meas_type = ''

        return


    def set_meas_type(self, m_type):
        '''Checks if m_type is in file and sets it to measurement type'''
        file_children = list(dict(self.h5file.root._v_children).keys())
        if m_type in file_children:
            self.meas_type = m_type
        else:
            print('Type not in file')
        return
    
    
    def get_meas_types(self):
        '''Returns all types of measurements present in h5file'''
        all_types = dict(self.h5file.root._v_children).keys()
        return list(all_types)


    def read_recent(self):
        '''Returns data of most recently logged measurement'''
        data = {}
        for node in self.h5file:
            if 'time' in node._v_attrs:
                data[node._v_pathname] = node._v_attrs['time']
        
        times = np.array(data.values())
        r_idx = np.argmin(times)
        recent = list(data.keys())[r_idx]
        
        return self.h5file.root[recent].read()
    
    
    def info_recent(self):
        '''Returns attributes of most recently logged measurement'''
        data = {}
        for node in self.h5file:
            if 'time' in node._v_attrs:
                data[node._v_pathname] = node._v_attrs['time']
        
        times = np.array(data.values())
        r_idx = np.argmin(times)
        recent = list(data.keys())[r_idx]
        
        return self.h5file.root[recent]._v_attrs
    
    
    def read_type(self, m_type):
        '''Read all from specified measurement type
            Returns dict of all data
        '''
        data = {}
        for node in self.h5file.root[m_type]._f_walknodes('Array'):
            pare_name = node._v_parent._v_name
            node_name = node._v_name
            data[pare_name][node_name] = node.read()
        
        return data
    
    
    def info_type(self, m_type):
        '''Returns dictionary of attribute set of each measurement 
            in specified type
        '''
        info  = {}
        for group in dict(self.h5file.root[m_type]._v_children).keys():
            info[str(group._v_name)] = group._v_attrs
            
        return info


        # End of Class
