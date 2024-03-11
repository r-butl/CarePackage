import ctypes

def cast_to_ctypes(data_list, type):
    array = (type * len(data_list))(*data_list)
    return array

def FIR(signal):

    def load_coeffs(file):
        values = list()
        with open(file, 'r') as f:        
            for line in f:
            # Convert each line to a float and append to the list
                coef = float(line.strip())
                values.append(coef)

        return values
    sampling_freq = 100
    # Coeffients depend on the frequency rate. Load the correct frequency coefficients.
    if sampling_freq == 500:
        coeffs = load_coeffs("./FIR_coefs_bandpass_500.csv")
    else:
        coeffs = load_coeffs("./FIR_coefs_bandpass_100.csv")

    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.convolution.argtypes = [  ctypes.POINTER(ctypes.c_float), 
                                        ctypes.POINTER(ctypes.c_float), 
                                        ctypes.POINTER(ctypes.c_float), 
                                        ctypes.c_int,
                                        ctypes.c_int]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal)), ctypes.c_float)
    functions.convolution(cast_to_ctypes(signal, ctypes.c_float),
                                  output_signal,
                                  cast_to_ctypes(coeffs, ctypes.c_float),  
                                  (len(signal)),
                                  len(coeffs))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list
    return output_signal

def fivepoint_diff(signal, sampling_freq):

    sampling_period = 1 / sampling_freq;
    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.fivepoint_diff.argtypes = [   ctypes.POINTER(ctypes.c_float),
                                            ctypes.POINTER(ctypes.c_float), 
                                            ctypes.c_int,
                                            ctypes.c_float]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal) - 4), ctypes.c_float)
    functions.fivepoint_diff(cast_to_ctypes(signal, ctypes.c_float),
                             output_signal,
                            (len(signal)),
                            ctypes.c_float(sampling_period))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list
    return output_signal

def pointwise_squaring(signal):

    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.squaring.argtypes = [ ctypes.POINTER(ctypes.c_float),
                                    ctypes.POINTER(ctypes.c_float), 
                                    ctypes.c_int]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal)), ctypes.c_float)

    functions.squaring(cast_to_ctypes(signal, ctypes.c_float),
                             output_signal,
                            (len(signal)))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list
    return output_signal

def moving_window_integration(signal):
    
    window_size = 20
    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.moving_window_integration.argtypes = [ctypes.POINTER(ctypes.c_float),
                                         ctypes.POINTER(ctypes.c_float), 
                                              ctypes.c_int,
                                              ctypes.c_int]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal)), ctypes.c_float)

    functions.moving_window_integration(cast_to_ctypes(signal, ctypes.c_float),
                             output_signal,
                            (len(signal)),
                            ctypes.c_int(window_size))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list
    return output_signal

def central_diff(signal, sampling_freq):

    sampling_period = 1 / sampling_freq;
    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  
    functions.central_diff.argtypes = [   ctypes.POINTER(ctypes.c_float),
                                            ctypes.POINTER(ctypes.c_float), 
                                            ctypes.c_int,
                                            ctypes.c_float]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal)), ctypes.c_float)
    functions.central_diff(cast_to_ctypes(signal, ctypes.c_float),
                             output_signal,
                            (len(signal)),
                            ctypes.c_float(sampling_period))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  
    return output_signal

def detect_QRS(signal):

    # Set up the function
    function = ctypes.CDLL('./pan_tompkins.so') 
    function.detect_QRS.argtypes = [    ctypes.POINTER(ctypes.c_float),
                                        ctypes.POINTER(ctypes.c_int),
                                        ctypes.c_int,
                                        ctypes.POINTER(ctypes.c_int)
                                    ]
    
    # Run it
    output_indices = cast_to_ctypes([0] * 100, ctypes.c_int)
    num_peaks = ctypes.c_int(0)

    function.detect_QRS(cast_to_ctypes(signal, ctypes.c_float),
                        output_indices,
                        len(signal),
                        ctypes.byref(num_peaks)
                        )
    
    output_indices = [output_indices[i] for i in range(len(output_indices))]
    return output_indices
