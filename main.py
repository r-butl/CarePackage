import ctypes

acc_func = ctypes.CDLL('./acc_func.so')
acc_func.low_pass.argtypes = [ctypes.POINTER(ctypes.c_int)]
acc_func.low_pass.restype = ctypes.POINTER(ctypes.c_int)


