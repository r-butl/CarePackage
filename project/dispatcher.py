import pandas as pd
import numpy as np
import wfdb
import multiprocessing as mp
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import json
import time
import ast

class data_dispatcher:

    # Signal Loading parameters
    sampling_rate = 100

    # Meta data state machine information
    signal_meta_data = []
    max_index = 0           # Total number of batches
    current_index = 0       # Current batch index
    signal_id = 0

    # Encryption Parameters
    block_size = 16

    # Important files for operation
    database_file = "ptbxl_database.csv"

    # Queues for stages
    Q_signals_to_load = mp.Queue()
    Q_ready_to_send = mp.Queue()

    def __init__(self, path, sampling_rate=100):
        """Reads signal meta data, sets up encryption and queues"""
        self.path = path

        with open(path+self.database_file, 'r') as file: 
            self.total_lines = sum(1 for line in file)
        
        # Set the sampling rate to determine which signal to load
        if sampling_rate != 100:
            self.sampling_rate = 500
        else:
            self.sampling_rate = 100

        #   Create the encryption unit
        self.key = os.urandom(32)   # 256-bit key
        self.iv = os.urandom(self.block_size)    # AES block size is 16 bytes
        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        self.padder = padding.PKCS7(self.block_size*8)

        # Load up initial meta data
        print("Loading up signal meta data...")
        records = pd.read_csv(self.path+self.database_file, index_col='ecg_id')
        records.scp_codes = records.scp_codes.apply(lambda x: ast.literal_eval(x)) # Not sure what this does, found it in the example

        for _, row in records.iterrows():
            self.signal_meta_data.append(row.to_dict())
        
        self.max_index = len(self.signal_meta_data)

    def reset(self):
        '''Resets the signal sending statemachine'''
        self.current_index = 0 
        self.signal_id = 0
    
    def generate_id(self):
        """Generates a unique ID for the signal being sent"""
        self.signal_id += 1
        return str(self.signal_id).zfill(7)

    def give_one_signal(self):
        # Grab a signal from the list
        record = self.signal_meta_data[self.current_index]
        self.current_index = self.current_index+1

        # Load in the raw signal
        if self.sampling_rate == 100:
            data = wfdb.rdsamp(self.path+record["filename_lr"])
        else:
            data = wfdb.rdsamp(self.path+record["filename_hr"])

        print(data)
        return data

    def prepare_signal(self):
        """Loads up signal from a file, preps it to be sent, pushes to Q_ready_to_send"""

        data = self.give_one_signal()

        # Construct the data packet
        data_packet = {
            'time_stamp'    :time.time(),
            'id'            :self.generate_id(),
            'sample_rate'   :self.sampling_rate,
            'signal_data'   :data[0].tolist()
        }

        # Serialize the data and Encrypt
        serialized_data = json.dumps(data_packet).encode('utf-8')

        # Pad the data
        padder = self.padder.padder()   # Must create a new context for each usage of the padder and encryptor
        serialized_data = padder.update(serialized_data) + padder.finalize()

        # Encrypt the data
        encryptor = self.cipher.encryptor()
        serialized_data = encryptor.update(serialized_data) + encryptor.finalize()   

        self.Q_ready_to_send.put(serialized_data)

    def connect_and_send(self):
        """Pops a packet off of Q_ready_to_send and sends it"""

        packet = self.Q_ready_to_send.get()

        return packet
    
    def test_run(self):
        self.prepare_signal()
        
