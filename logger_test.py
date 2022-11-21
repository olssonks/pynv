import numpy as np

from utils.data_logger import Logger

from utils.measurement_types import measurement_types, types_data

import time

data = np.load('data/test_data.npy')

data = np.stack(data.reshape(2,10, 10000), axis=1)

#data=np.random.random((2, 1024))

file_name = 'ODMR-1.h5'

m_type = 'ODMR'

data_genres = ['raw']

configs = {'meas': 1}

record = Logger(file_name, config= configs)
record.set_meas_type(m_type)

info = {'units': ['MHz','mV']}

#record.log_data(data, data_genres[0], info=info)

for d in data:
    print(d.shape)
    record.log_data(d, data_genres[0], info=info)

record.h5file.flush()

record.h5file.close()