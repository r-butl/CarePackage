import dispatcher as d
from matplotlib import pyplot as plt
import ctypes

    
def plot_signals(signals):
    if type(signals) != list:
        print("argument must be in list format")
        return
        
    for i in range(len(signals)):
        plt.subplot(len(signals), 1, i+1)  # Two rows, one column, first plot
        plt.plot([j for j in range(len(signals[i]))], signals[i])
        plt.xlim([0, 1100])

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

if __name__ == "__main__":

    data_source = d.data_dispatcher(path="/home/lucas/Desktop/programming/Senior_project/project/data/",
                                    sampling_rate=500)

    signals = list()
    signals.append([i[0] for i in data_source.give_one_signal()[0].tolist()])
    

    coeffs = load_coeffs("./FIR_coefs_bandpass_5_15.csv")

    # Set up the function
    functions = ctypes.CDLL('./pan_tompkins.so')  # Use 'example.dll' on Windows
    #functions.bandpass_fir_filter.restype = ctypes.POINTER(ctypes.c_float)
    functions.bandpass_fir_filter.argtypes = [ctypes.POINTER(ctypes.c_float), 
                                              ctypes.POINTER(ctypes.c_float), 
                                              ctypes.POINTER(ctypes.c_float), 
                                              ctypes.c_int,
                                              ctypes.c_int]

    # run it
    output_signal = cast_to_ctypes([0.0] * (len(signals[0])))
    print(f"coefs {len(coeffs)} insig: {len(signals[0])} output: {len(output_signal)}")
    functions.bandpass_fir_filter(cast_to_ctypes(signals[0]),
                                  output_signal,
                                  cast_to_ctypes(coeffs),  
                                  (len(signals[0])),
                                  len(coeffs))
    
    output_signal = [output_signal[i] for i in range(len(output_signal))]  # Get the returned list point into a python list
    #print(output_signal)
    #for i, y in zip(signals[0], output_signal):
        #print(i, y)

    signals.append(output_signal)

    plot_signals(signals)
    