import dispatcher as d
from matplotlib import pyplot as plt
import ctypes

    
def plot_signals(signals, xlim):
    if type(signals) != list:
        print("argument must be in list format")
        return
        
    for i in range(len(signals)):
        plt.subplot(len(signals), 1, i+1)  # Two rows, one column, first plot
        plt.plot([j for j in range(len(signals[i]))], signals[i])
        plt.xlim([0, xlim])

    plt.show()

def load_coeffs(file):
    values = list()
    with open(file, 'r') as f:        
        for line in f:
        # Convert each line to a float and append to the list
            coef = float(line.strip())
            values.append(coef)

    return values

def cast_to_ctypes(data_list):
    array = (ctypes.c_float * len(data_list))(*data_list)
    return array

def FIR(signal):

    if sampling_freq == 500:
        coeffs = load_coeffs("./FIR_coefs_bandpass_500.csv")
    elif sampling_freq == 100:
        coeffs = load_coeffs("./FIR_coefs_bandpass_100.csv")


    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.convolution.argtypes = [ctypes.POINTER(ctypes.c_float), 
                                              ctypes.POINTER(ctypes.c_float), 
                                              ctypes.POINTER(ctypes.c_float), 
                                              ctypes.c_int,
                                              ctypes.c_int]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal)))

    print(f"coefs {len(coeffs)} insig: {len(signal)} output: {len(output_signal)}")
    functions.convolution(cast_to_ctypes(signal),
                                  output_signal,
                                  cast_to_ctypes(coeffs),  
                                  (len(signal)),
                                  len(coeffs))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list

    return output_signal

def fivepoint_diff(signal, sampling_freq):

    sampling_period = 1 / sampling_freq;
    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.fivepoint_diff.argtypes = [ctypes.POINTER(ctypes.c_float),
                                         ctypes.POINTER(ctypes.c_float), 
                                              ctypes.c_int,
                                              ctypes.c_float]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal) - 4))

    functions.fivepoint_diff(cast_to_ctypes(signal),
                             output_signal,
                            (len(signal)),
                            ctypes.c_float(sampling_period))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list

    return output_signal

def pointwise_squaring(signal):

    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    functions.squaring.argtypes = [ctypes.POINTER(ctypes.c_float),
                                         ctypes.POINTER(ctypes.c_float), 
                                              ctypes.c_int]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signal)))

    functions.squaring(cast_to_ctypes(signal),
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
    output_signal = cast_to_ctypes([0.0] * (len(signal)))

    functions.moving_window_integration(cast_to_ctypes(signal),
                             output_signal,
                            (len(signal)),
                            ctypes.c_int(window_size))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list

    return output_signal


def pipeline(signals):
        # Apply FIR filter
    signals.append(FIR(signals[-1]))
    signals.append(fivepoint_diff(signals[-1], sampling_freq))
    signals.append(pointwise_squaring(signals[-1]))
    signals.append(moving_window_integration(signals[-1]))

    return signals


if __name__ == "__main__":

    sampling_freq = 100
    data_source = d.data_dispatcher(path="/home/lucas/Desktop/programming/Senior_project/project/data/",
                                    sampling_rate=sampling_freq)

    # Look at some signals
    signals = list()
    for i in range(4): signals.append([i[0] for i in data_source.give_one_signal()[0].tolist()])
    #plot_signals(signals)


    # Apply pipeline to one
    signals = list()
    signals.append([i[0] for i in data_source.give_one_signal()[0].tolist()])
    signals = pipeline(signals)

    length_limit = 200
    plot_signals(signals, length_limit)

    