import pandas as pd
import numpy as np
import wfdb
import ast

def load_raw_data(df, sampling_rate, path):
    if sampling_rate == 100:
        data = [wfdb.rdsamp(path+f) for f in df.filename_lr]
    else:
        data = [wfdb.rdsamp(path+f) for f in df.filename_hr]
    data = np.array([signal for signal, meta in data])
    return data

path = '/home/lucas/Desktop/Senior_project/ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.3/'
sampling_rate=100

# load and convert annotation data
Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')
Y.scp_codes = Y.scp_codes.apply(lambda x: ast.literal_eval(x))

# Load raw signal data
X = load_raw_data(Y, sampling_rate, path)

# Signal, Timestep, value for each of the 12 leads
sig = [X[0][i][0] for i in range(len(X[0]))]
print(len(sig))


from scipy.fft import fft, ifft
fft_sig = fft(sig)

import matplotlib.pyplot as plt
plt.xlabel("Time (milliseconds)")
plt.ylabel("Voltage (millivolts)")
plt.show()