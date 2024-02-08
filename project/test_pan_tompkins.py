import ctypes
import numpy as np
import wfdb
import pandas as pd
import dispatcher as d

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
    

if __name__ == "__main__":

    data_source = d.data_dispatcher(path="/home/lucas/Desktop/programming/Senior_project/project/data/",
                                    sampling_rate=100)

    signal = [i[0] for i in data_source.give_one_signal()[0].tolist()]

    print(signal)