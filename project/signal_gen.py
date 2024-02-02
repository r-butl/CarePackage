import pandas as pd
import numpy as np
import wfdb
import ast
import time
import multiprocessing as mp

def views_signal(signal):
    # Signal, Timestep, value for each of the 12 leads
    sig = [signal[0][i][0] for i in range(len(X[0]))]
    print(len(sig))


    from scipy.fft import fft, ifft
    fft_sig = fft(sig)

    import matplotlib.pyplot as plt
    plt.plot(sig)
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Voltage (millivolts)")
    plt.show()

class data_dispatch:

    batch_size = 1000        # Size of each signal batch
    max_index = 0           # Total number of batches
    current_index = 0       # Current batch index
    total_lines = 0
    sampling_rate = 100

    # Important files for operation
    database_file = "ptbxl_database.csv"

    Q_signals_to_load = mp.Queue()
    Q_ready_to_send = mp.Queue()

    def __init__(self, path):
        """Reads the records database and calculates the number of batches used in the engine"""
        with open(path+self.database_file, 'r') as file: 
            self.total_lines = sum(1 for line in file)
        
        self.max_index = int(np.ceil(self.total_lines / self.batch_size)) - 1 # Store the maximum index
        self.path = path

    def reset(self):
        self.current_index
        self.Q_ready_to_send = mp.Queue()
        self.Q_ready_to_send = mp.Queue()
    
    def queue_signals_to_process(self):
        """Reads a batch size of meta information and returns a dataframe of it"""

        # Check the length of the queue
        if self.Q_signals_to_load.qsize() < int(self.batch_size * 0.5):

            # For reusing the database signals continuous, will reset when the end of the database is reached
            if self.current_index < self.max_index:
                self.current_index += 1
            else:
                print("End of database reached, resetting index...")
                self.current_index = 0

            # Reads a batch of signal meta data and pushes it to the queue
            print(f"___________________________________________\nCurrent index: {self.current_index}, Max Index: {self.max_index},  \nCurrent line:  {self.current_index * self.batch_size} Total Lines: {self.total_lines}")
            records = pd.read_csv(self.path+self.database_file, index_col='ecg_id', skiprows=range(1, self.current_index*self.batch_size), nrows=self.batch_size)
            #records.scp_codes = records.scp_codes.apply(lambda x: ast.literal_eval(x)) # Not sure what this does, found it in the example

            for _, row in records.iterrows():
                self.Q_signals_to_load.put(row.to_dict())
        else:   # Load queue has plenty of records
            return

    def prep_to_send(self):
        """Loads up signal from a file, preps it to be sent, pushes to Q_ready_to_send"""

        record = self.Q_signals_to_load.get()
        print("\n\n" ,record)
        def load_raw_data(df, sampling_rate, path):
            if sampling_rate == 100:
                data = [wfdb.rdsamp(path+f) for f in df.filename_lr]
            else:
                data = [wfdb.rdsamp(path+f) for f in df.filename_hr]
            data = np.array([signal for signal, meta in data])
            return data
            
            #signals = load_raw_data(records, self.sampling_rate, self.path)
            #eturn signals


def time_dispatch(num_elements, dispatcher):
    import time
    start_time = time.time()
    for _ in range(num_elements):
        dispatcher.queue_signals_to_process()
        dispatcher.prep_to_send()

    elasped_time = time.time() - start_time
    print(f"---- {num_elements} signals in {elasped_time} seconds ----")
    dispatcher.reset()
    return elasped_time

if __name__ == "__main__":
    path = '/home/lucas/Desktop/Senior_project/data/'
    dispatcher = data_dispatch(path)

    times = list()
    test_count = 30
    for _ in range(test_count):
        times.append(time_dispatch(10000, dispatcher))

    from matplotlib import pyplot as plt
    plt.scatter([i for i in range(test_count)], times)
    plt.title("Batch Size: 1000")
    plt.xlabel("Trials")
    plt.ylabel("Time (seconds)")
    plt.show()
