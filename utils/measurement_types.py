# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 08:48:02 2022

@author: walsworth1
"""

measurement_types = ['ODMR', 'Rabi', 'Ramsey', 'AC', 'T1', 'Other']

types_data = {
    'ODMR': ['freq', 'pl'],
    'RABI': ['duration', 'pl'],
    'RAMSEY': ['tau', 'pl'],
    'AC': ['tau', 'pl'],
    'T1': ['tau', 'pl'],
    'OTHER': ['x', 'y']
}
