import ctypes
import numpy as np

def give_array(input):

    out = map(ctypes.c_int, input)
    return out

acc_func = ctypes.CDLL('./acc_func.so')
acc_func.wavelet.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
acc_func.wavelet.restype = ctypes.POINTER(ctypes.c_int)


arr1 = np.array([1.0]* 10, dtype=ctypes.c_int8)
print(arr1)
#print(arr1, give_array(arr1))
give_array(arr1)
sample_rate = 100
corner_freq = 10

#acc_func.low_pass(give_array(arr1), sample_rate, corner_freq)