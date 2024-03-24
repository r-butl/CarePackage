import pandas as pd
import wfdb
import os
import ast
import sys

############################################################################################        

# Data controller 
class DataController:

    # Signal Loading parameters
    sampling_freq = 100

    # Meta data state machine information
    signal_meta_data = []
    max_index = 0           # Total number of batches
    current_index = 0       # Current batch index
    signal_id = 0

    # Expects the ptbxl_database.csv file path
    required = ['ptbxl_database.csv', 'records100', 'records500']


    def __init__(self, path, sampling_freq=100):
        """Reads signal meta data, sets up encryption and queues"""
        self.path = path

        if not set(self.required).issubset(set(os.listdir(path))):
            sys.exit("Invalid data source, expecting: ptbxl_database.csv")

        with open(path+self.required[0], 'r') as file: 
            self.total_lines = sum(1 for line in file)
        
        # Set the sampling rate to determine which signal to load
        if sampling_freq != 100:
            self.sampling_freq = 500
        else:
            self.sampling_freq = 100

        # Load up initial meta data
        records = pd.read_csv(self.path+self.required[0], index_col='ecg_id')
        records.scp_codes = records.scp_codes.apply(lambda x: ast.literal_eval(x)) # Not sure what this does, found it in the example

        for _, row in records.iterrows():
            self.signal_meta_data.append(row.to_dict())
        
        self.max_index = len(self.signal_meta_data)

    def reset(self):
        '''Resets the signal sending statemachine'''
        self.current_index = 0 
        self.signal_id = 0
    
    def give_signal(self, only_one=True):
        # Grab a signal from the list
        if self.current_index + 1 == self.max_index:
            self.current_index = 0
        else:
            self.current_index = self.current_index+1
        
        record = self.signal_meta_data[self.current_index]

        # Load in the raw signal
        if self.sampling_freq == 100:
            data = wfdb.rdsamp(self.path+record["filename_lr"])
        else:
            data = wfdb.rdsamp(self.path+record["filename_hr"])

        # Serve one or multiple Leads
        if only_one:
            return [i[0] for i in data[0].tolist()]
        else:
            return data
        
