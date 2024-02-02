import ctypes
import numpy as np
import wfdb
import pandas as pd

# Initiate Accelerator Functions
class accelerator:

    def __init__(self):
        acc_func = ctypes.CDLL('./acc_func.so')
        acc_func.median.argtypes = ctypes.POINTER(ctypes.c_int)
        acc_func.median.restype = ctypes.POINTER(ctypes.c_int)

    def median(self, input):
        return None
    
    def wavelet(self, input):
        return None

def load_raw_data(df, sampling_rate, path):
    if sampling_rate == 100:
        data = [wfdb.rdsamp(path+f) for f in df.filename_lr]
    else:
        data = [wfdb.rdsamp(path+f) for f in df.filename_hr]
    data = np.array([signal for signal, meta in data])
    return data

path = '/home/lucas/Desktop/Senior_project/data/'
Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')
