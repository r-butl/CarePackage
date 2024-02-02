import pandas as pd
import numpy as np
import wfdb
import multiprocessing as mp

class data_dispatcher:

    batch_size = 1000        # Size of each signal batch
    max_index = 0           # Total number of batches
    current_index = 0       # Current batch index
    total_lines = 0
    sampling_rate = 100

    # Important files for operation
    database_file = "ptbxl_database.csv"

    Q_signals_to_load = mp.Queue()
    Q_ready_to_send = mp.Queue()

    def __init__(self, path, batch_size=100, sampling_rate=100):
        """Reads the records database and calculates the number of batches used in the engine"""
        with open(path+self.database_file, 'r') as file: 
            self.total_lines = sum(1 for line in file)
        
        if sampling_rate != 100:
            self.sampling_rate = 500
        else:
            self.sampling_rate = 100
        self.batch_size = batch_size
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
        #print("\n\n" ,record)

        # Load in the raw signal
        if self.sampling_rate == 100:
            data = wfdb.rdsamp(self.path+record["filename_lr"])
        else:
            data = wfdb.rdsamp(self.path+record["filename_hr"])

        print(data[0])

    def send_signal(self):
        """Sends a """
        pass

    def run(self):
        self.queue_signals_to_process()
        self.prep_to_send()


