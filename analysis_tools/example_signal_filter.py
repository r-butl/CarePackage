import pandas as pd
import numpy as np
import wfdb
import ast
import math

def give_one_signal():
    def load_raw_data(df, sampling_rate, path):
        if sampling_rate == 100:
            data = [wfdb.rdsamp(path+f) for f in df.filename_lr]
        else:
            data = [wfdb.rdsamp(path+f) for f in df.filename_hr]
        data = np.array([signal for signal, meta in data])
        return data

    path = '/home/lucas/Desktop/Senior_project/data/'
    sampling_rate=500
    Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')
    print(Y)
    Y.scp_codes = Y.scp_codes.apply(lambda x: ast.literal_eval(x))

    X = wfdb.rdsamp(path+Y['filename_hr'].iloc[0])

    sig = [X[0][i][0] for i in range(len(X[0]))]
    return sig

def convert_to_digital(corner_freq, sample_freq):
    # Biinear transform
    return 2 * math.atan((2 * math.pi * corner_freq)/(2 * sample_freq))

def attentuation(reduction_percentage):
    return 20 * math.log10(1 - reduction_percentage)

def give_coefs():
    # https://www.allaboutcircuits.com/technical-articles/design-examples-of-fir-filters-using-window-method/
    sample_freq = 500      # hz

    band_pass = False
    lower_pass_band = convert_to_digital(0, sample_freq)         # hz
    lower_stop_band = convert_to_digital(10, sample_freq)         # hx
    lower_corner = (lower_stop_band + lower_pass_band) / 2

    upper_pass_band = convert_to_digital(30, sample_freq)         # hz
    upper_stop_band = convert_to_digital(50, sample_freq)         # hx
    upper_corner = (upper_stop_band + upper_pass_band) / 2

    delta_2 = attentuation(.999)    # Stop band reduction

    # Determins order based on window type
    mainloab_coef = float()

    if delta_2 > -21:   # rectangular
        mainloab_coef = 4 * math.pi
    elif delta_2 > -44: # hanning
        mainloab_ceof = 8 * math.pi
    elif delta_2 > -53: # hamming
        mainloab_coef = 8 * math.pi
    elif delta_2 > -74: # blackman
        mainloab_coef = 12 * math.pi
    else:
        print("Attentuation unachievable with currently available windows")
        exit()

    # Compute Order
    upper_order = math.ceil(mainloab_coef / (abs(upper_pass_band - upper_stop_band))) - 1
    lower_order = math.ceil(mainloab_coef / (abs(lower_pass_band - lower_stop_band))) - 1

    # Take the larger order for computing the coeffiencients
    if band_pass: 
        order = max(upper_order, lower_order)
    else:
        order = upper_order

    # Subtracts the upper sinc coefficient from the lower sinc coefficient
    def compute_coef(w_u, w_l, order, n, band=True):
        lower = (w_l/math.pi) * np.sinc(w_l * (n - order/2) / math.pi) if band else 0
        return (w_u/math.pi) * np.sinc(w_u * (n - order/2) / math.pi) - lower

    coefs = [compute_coef(upper_corner, lower_corner, order, i, band_pass) for i in range(order)]
    return coefs

def median_filter(signal):
    window_size = 10
    output_signal = np.zeros(len(signal) - window_size)
    for i in range(window_size, len(signal)):
        output_signal[i - window_size] = np.median(signal[i-window_size:i])

    return output_signal


from matplotlib import pyplot as plt
from scipy import signal as s

signal = give_one_signal()
coefs = give_coefs()

convolved = np.convolve(signal, coefs)
median = median_filter(convolved)

# frequency response
w, h = s.freqz(coefs, worN=1024)

# Output of the s.freqz is normalized with the nyquist 
target_upper = convert_to_digital(35, 500) / (2 * np.pi)
target_lower = convert_to_digital(10, 500) / (2 * np.pi)
print(target_lower, target_upper)

# First plot (stem plot)
plt.figure(figsize=(10, 6))  # Create a figure

# Stem plot for coefficients
plt.subplot(3, 1, 1)  # Two rows, one column, first plot
plt.title(f'Filter Order = {len(coefs)} Latency = {len(coefs)/500}s')
plt.stem([i for i in range(-int(len(coefs)/2), math.ceil(len(coefs)/2) , 1)], coefs)
plt.xlim([-100, 100])

# Second plot (overlayed signal and convolved)
plt.subplot(3, 1, 2)  # Two rows, one column, second plot
plt.plot([i for i in range(len(signal))], [signal[int(len(coefs)/500) + i] for i in range(len(signal))], label='Signal', color='blue')
plt.plot([i for i in range(len(convolved))], convolved, label='Convolved', color='orange')
#plt.plot([i for i in range(len(median))], median, label='Median', color='red')

plt.xlim([0, 2000])
plt.legend()

# Frequency response of the filter
plt.subplot(3, 1, 3)
plt.title(f"Target Corners: {round(target_upper,3)}, {round(target_lower, 3)} in radians")
plt.plot(w/(2*np.pi), np.abs(h))
plt.axvline(x = target_upper, color='r')
plt.axvline(x = target_lower, color='g')
plt.xlabel('Frequency (radians)')
plt.xlim([0, .4])
plt.tight_layout()  # Adjust the layout
plt.show()  # Display the figure