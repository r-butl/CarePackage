#           Lucas Butler
#           Process Block abstraction layer:
#               here you will find the template for the process block class as well
#               as various implementations of the process block using the different
#               functions defined in pan_tompkins

import CarePackage
from abc import ABC, abstractmethod

class ProcessBlock(ABC):

    def __init__(self, next_filter=None, observer=None, peaks = False):
        self.info = {}  
        self.next_filter = None
        self.observers = []
        self.function = None
        self.peaks = None
        self.initialize()

    @abstractmethod
    def initialize(self):
        """ Initialize subclass specific settings like function and info. """
        pass

    def process(self, signal):
        ''' Executes the process block'''
        if self.function:
            signal = self.function(signal)

        # Send the signal information to the plots that are observing the process block
        for observer in self.observers:
            indices = None
            if self.peaks:
                indices = CarePackage.detect_peak(signal, 0.65)
            observer.update_signal(signal, indices)

        return signal

    def set_info(self, option, value):
        ''' Sets the configurable parameters of the process block'''
        if option in self.info and type(value) == type(self.info[option]):
            self.info[option] = value

    def set_next_filter(self, filter):
        self.next_filter=filter

    def remove_next_filter(self):
        self.next_filter=None

class FIR(ProcessBlock):
    def initialize(self):  
        self.info = {
            'name' : 'FIR Filter',
            'uuid' : None,
            'peaks' : False,
            'coefs': []
        }
        self.function = lambda signal: CarePackage.FIR(signal, self.info['coefs'])

class FPD(ProcessBlock):
    def initialize(self):        
        self.info = {
            'name' : 'Five Point Differential',
            'uuid' : None,
            'peaks' : False,
            'sampling_freq': 100
        }
        self.function = lambda signal: CarePackage.FPD(signal, self.info['sampling_freq'])

class PS(ProcessBlock):
    def initialize(self):  
        self.info = {
            'name' : 'Pointwise Squaring',
            'uuid' : None,
            'peaks' : False,
        }

        self.function = lambda signal: CarePackage.pointwise_squaring(signal)

class MWI(ProcessBlock):
    def initialize(self):  
        self.info = {
            'name' : "Moving Window Integration",
            'uuid' : None,
            'peaks' : False,
            'window_size' : 20
        }

        self.function = lambda signal: CarePackage.moving_window_integration(signal, self.info['window_size'])

class CD(ProcessBlock):
    def initialize(self):  
        self.info = {
            'name' : 'Central Differential',
            'uuid' : None,
            'peaks' : False,
            'sampling_freq' : 100
        }

        self.function = lambda signal: CarePackage.central_diff(signal, self.info['sampling_freq'])
