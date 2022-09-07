# Kevin Olsson
# Last updated: Sep 06 2022

import numpy as np
import tables

config_file = ''


class Logger:

    def __init__(self, file_name, config=config_file):
        ## default compression settings
        self.complevel = 5
        self.complib = 'blosc'
        self.bitshuffle = True

        self.meas_type = self.get_meas_type(file_name)
        self.meas_num = 0

        self.file_name = file_name
        self.h5file = self.get_file(self.file_name)
        self.data_location = self.set_loc(config)

        self.expectedrows = 512
        self.atom = tables.Atom.from_sctype('float64')
        self.chunksize = (512, 256)

        self.current_arrays = {}

        return

    def get_file(self, name):
        filt = tables.Filters(complevel=self.complevel,
                              complib=self.complib,
                              bitshuffle=self.bitshuffle)

        if not '.h5' == name[-3:]:
            name = name + '.h5'

        file = tables.open_file(name, mode='a', filters=filt)
        return file

    def get_meas_type(self, name):
        '''Check name for type of measurement'''
        type_idx = np.where([(type in name)
                             for type in measurement_types])[0][0]
        return measurement_types[type_idx]

    def set_loc(self, meas_config):
        '''
        Gets type of measurement from file name, then checks/makes group for
        this type of measurement. Creates group for the nth measurement of this 
        type, with 0 indexing, and saves the configurate as an attribute.
        Example: New Rabi measurement
        location: '/Rabi/Rabi000'
        Example: 5th ODMR measurment
        location: '/ODMR/ODMR004'

        '''

        m_type = self.meas_type

        if self.h5file.__contains__('/' + m_type):
            self.meas_type = m_type
            meas = self.h5file.root['/' + m_type]
            self.meas_num = len(dict(meas._v_children).keys())
            loc = self.h5file.create_group(meas,
                                           m_type + f'{self.meas_num:03d}')
            self.h5file.set_node_attr(loc, 'config', meas_config)
            self.meas_type = m_type
            self.meas_num = self.meas_num + 1
        else:
            loc = self.h5file.create_group(self.file.root, m_type)
            self.meas_num = 0
            loc = self.h5file.create_group(meas,
                                           m_type + f'{self.meas_num:03d}')
            self.meas_type = m_type
            self.meas_num = 1

        return loc

    def log_raw(self, data, info=''):

        if not self.h5file.__contains__(self.data_location + '/raw'):
            dshape = list(data.shape)
            array_shape = [0].append(dshape)
            self.current_array['raw'] = self.h5file.creat_earray(
                self.data_location,
                'raw',
                atom=self.atom,
                shape=array_shape,
                expectedrows=self.expectedrows)
        self.current_array['raw'].append(data)
        if not len(info):
            self.set_node_attr(self.current_array, 'info', info)

        return

    def log_reduced(self, data, info=''):

        if not self.file.__contains__(self.data_location + '/reduced'):
            dshape = list(data.shape)
            array_shape = [0].append(dshape)
            self.current_array['reduced'] = self.h5file.creat_earray(
                self.data_location,
                'reduced',
                atom=self.atom,
                shape=array_shape,
                expectedrows=self.expectedrows)
        self.current_array[reduced].append(data)
        if not len(info):
            self.set_node_attr(self.current_array, 'info', info)

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


### End of Class

### Helper Functions

measurement_types = ['ODMR', 'Rabi', 'Ramsey', 'AC', 'T1', 'Other']

types_data = {
    'ODMR': ['freq', 'pl'],
    'RABI': ['duration', 'pl'],
    'RAMSEY': ['tau', 'pl'],
    'AC': ['tau', 'pl'],
    'T1': ['tau', 'pl'],
    'OTHER': ['x', 'y']
}
