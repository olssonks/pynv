import numpy as np

from utils.data_logger import Logger

from utils.measurement_types import measurement_types, types_data

import time

file_name = 'ODMR-1.h5'

m_type = 'ODMR'

data_genres = ['raw']

configs = {'meas': 1}

record = Logger(file_name, config= configs)
record.set_meas_type(m_type)

info = {'units': ['MHz','mV']}

data = np.random.random((128,1024))
record.log_data(data, data_genres[0], info=info)

data = np.random.random((128,1024))
record.log_data(data, data_genres[0], info=info)

data = np.random.random((128,1024))
record.log_data(data, data_genres[0], info=info)

record.h5file.flush()

record.h5file.close()