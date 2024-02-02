import pandas as pd
import numpy as np
import wfdb
import multiprocessing as mp
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import json

class data_dispatcher:

    # Signal Loading parameters
    batch_size = 1000        # Size of each signal batch
    max_index = 0           # Total number of batches
    current_index = 0       # Current batch index
    total_lines = 0
    sampling_rate = 100

    # Encryption Parameters
    block_size = 16

    # Important files for operation
    database_file = "ptbxl_database.csv"

    Q_signals_to_load = mp.Queue()
    Q_ready_to_send = mp.Queue()

    def __init__(self, path, batch_size=100, sampling_rate=100):
        """Reads the records database and calculates the number of batches used in the engine"""
        with open(path+self.database_file, 'r') as file: 
            self.total_lines = sum(1 for line in file)
        
        # Parameters for signal loading and optimizing speed
        if sampling_rate != 100:
            self.sampling_rate = 500
        else:
            self.sampling_rate = 100
        self.batch_size = batch_size
        self.max_index = int(np.ceil(self.total_lines / self.batch_size)) - 1 # Store the maximum index
        self.path = path

        #   Create the encryption unit
        self.key = os.urandom(32)   # 256-bit key
        self.iv = os.urandom(self.block_size)    # AES block size is 16 bytes
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        self.encryptor = cipher.encryptor()
        self.padder = padding.PKCS7(self.block_size*8).padder()

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

    def prep_signals_to_send(self):
        """Loads up signal from a file, preps it to be sent, pushes to Q_ready_to_send"""

        record = self.Q_signals_to_load.get()
        #print("\n\n" ,record)

        # Load in the raw signal
        if self.sampling_rate == 100:
            data = wfdb.rdsamp(self.path+record["filename_lr"])
        else:
            data = wfdb.rdsamp(self.path+record["filename_hr"])

        # Construct the data packet
        data_to_encrypt = data[0].tolist()
            

        # Serialize the data and Encrypt
        serialized_data = json.dumps(data_to_encrypt).encode('utf-8')
        # Pad the data before sending
        serialized_data = self.padder.update(serialized_data) + self.padder.finalize()
        # Data is encrypted in blocks, any remaining data is finished and added
        serialized_data = self.encryptor.update(serialized_data) + self.encryptor.finalize()   

        self.Q_ready_to_send.put(serialized_data)

    def send_signal(self):
        """Pops a packet off of Q_ready_to_send and sends it"""

        packet = self.Q_ready_to_send.get()

        print(packet)

    def run(self):
        self.queue_signals_to_process()
        self.prep_signals_to_send()
        self.send_signal()


