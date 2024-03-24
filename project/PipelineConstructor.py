import CarePackage
from abc import ABC, abstractmethod

#################################################################################

class ProcessBlock(ABC):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter

    @abstractmethod
    def process(self, signal):
        ''' Executes the process block'''
        pass

    def get_options(self):
        ''' Returns the configurable parameters of the process block'''
        return self.options

    def set_options(self, option, value):
        ''' Sets the configurable parameters of the process block'''
        if option in self.options and type(value) == type(self.options[option]):
            self.options[option] = value

    def set_next_filter(self, filter):
        self.next_filter=filter

class FIR(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : 'FIR Filter',
            'peaks' : False,
            'coefs': []
        }

    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.FIR(signal, self.options['coefs'])

class FPD(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : 'Five Point Differential',
            'peaks' : False,
            'sampling_freq': 100
        }
    
    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.FPD(signal, self.options['sampling_freq'])

class PointwiseSquaring(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : 'Pointwise Squaring',
            'peaks' : False,
        }

    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.pointwise_squaring(signal)


class MWI(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : "Moving Window Integration",
            'peaks' : False,
            'window_size' : 20
        }

    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.moving_window_integration(signal, self.options['window_size'])

class CD(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : 'Central Differential',
            'peaks' : False,
            'sampling_freq' : 100
        }

    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.central_diff(signal, self.options['sampling_freq'])

#################################################################################

class PipelineController:
    def __init__(self, sampling_freq):
        self.process_options = [
            CD(),
            PointwiseSquaring(),
            MWI()
        ]

        self.update_sampling_rate(sampling_freq)
        
    def process_signal(self, signalPlotController, signal):

        signalPlotController.add_signal(signal, "Base Signal", [])
        for p in self.process_options:
            signal = p.process(signal)
            signalPlotController.add_signal(signal, 
                                  p.get_options()['name'], 
                                  CarePackage.detect_peak(signal, 0.65) if p.get_options()['peaks'] else [])
            
    def update_sampling_rate(self, new_rate):
        self.sampling_freq = new_rate

        # Preset the process blocks with the data configuration for testing
        for i in self.process_options:
            i.set_options('sampling_freq', self.sampling_freq)


