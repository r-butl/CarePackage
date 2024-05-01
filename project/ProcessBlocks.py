#           Lucas Butler
#           Process Block abstraction layer:
#               here you will find the template for the process block class as well
#               as various implementations of the process block using the different
#               functions defined in pan_tompkins

import CarePackage
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import (
                             QWidget,
                             QVBoxLayout,
                             QPushButton,
                             QSizePolicy,
                             QHBoxLayout,
                             QCheckBox,
                             QLabel,
                             QDialog,
                             QDialogButtonBox
                             )
from TuneCoeffs import *

class ProcessBlock(ABC):

    def __init__(self, parent=None, next_filter=None, observer=None):
        self.parent = parent
        self.next_filter = None
        self.observers = []
        self.function = None
        self.signal = []
        self.signal_prev_stage = []
        self.indices = []
        self.initialize()

    @abstractmethod
    def initialize(self):
        """ Initialize subclass specific settings like function and info. """
        pass

    def process(self, signal=None):
        ''' Executes the process block'''
        #print(self.info['uuid'])
        if 'coefs' in self.info.keys():
            #print(self.info['coefs'])
            pass
        if signal != None:
            self.signal_prev_stage = signal

        if self.signal_prev_stage or self.signal:
            self.signal = self.function(self.signal_prev_stage)

            #print(f"Signal: {np.average(signal)}")
            if self.info['peaks'] == True:
                self.indices = CarePackage.detect_peak(self.signal, 75)
            else:
                self.indices = []

            # Send the signal information to the plots that are observing the process block
            for observer in self.observers:
                observer.update_signal(self.signal, self.indices)

            if self.next_filter:
                self.next_filter.process(self.signal)
                
    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def update_info(self, option, value):
        '''Used to update info in the process blocks'''
        if option in self.info:
            if isinstance(self.info[option], type(value) ):
                self.info[option] = value
                #print(f"block {self.info['uuid']} update {option} -> {self.info[option]}")
            else:
                print("ERROR: Process Block - Mismatch value for option")
        else:
            print(f"Key {option} not found, adding to self.info")
            self.info[option] = value

        # Signal to the pipeline model to reprocess 
        if self.parent:
            self.parent.process_signal()
        
    def show_option_panel(self):
        """ Defines a popup window for the options panel"""
        dialog = QDialog()
        dialog.setWindowTitle("Configuration Options")
        
        def accept():
            self.process()
            dialog.accept()

        layout = QVBoxLayout(dialog)

        for option, value in self.info.items():
            if option in ['name', 'uuid', 'sampling_freq']:
                continue
            optionWidget = self._create_option_widget(option, value)
            if optionWidget:
                layout.addWidget(optionWidget)

        applyButton = QDialogButtonBox(QDialogButtonBox.Apply)
        applyButton.button(QDialogButtonBox.Apply).clicked.connect(accept) 
        layout.addWidget(applyButton)

        dialog.exec_()

    def _create_option_widget(self, option, value):
        """Creates an options widget using the options in self.info"""
        optionWidget = None
        # Check what data type the option is and set it accordingly
        if option == 'peaks':
            optionWidget = QCheckBox()
            optionWidget.setChecked(value)
            optionWidget.stateChanged.connect(lambda state, opt=option: self.update_info(opt, bool(state)))
        elif isinstance(value, str) and value == "TunerModule":
            optionWidget = TunerModule(signal=self.signal_prev_stage if self.signal_prev_stage else self.signal, update_info_callback=self.update_info, filter_options=self.info)
            return optionWidget
        else:
            return

        # Create a container widget for the option
        optionContainer = QWidget()
        optionContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        optionLayout = QHBoxLayout(optionContainer)

        # Correct the label
        option = option.split('_')
        option = ' '.join(word.capitalize() for word in option)
        optionLabel = QLabel(option)
        optionLayout.addWidget(optionLabel)
        optionLayout.addWidget(optionWidget)

        # Add styles to customize appearance
        optionContainer.setStyleSheet("""
            QFrame {
                margin: 5px; 
            }

            QCheckBox, QSpinBox {
                background-color: #f0f0f0; 
            }
        """)

        return optionContainer
    
    def create_option_ui(self, add_block_callback):
        """Creates the UI for the process block in the option panel"""
        blockContainer = QWidget()
        blockLayout = QVBoxLayout(blockContainer)

        name = QLabel(self.info['name'])
        blockLayout.addWidget(name)

        # Option button
        optionButton = QPushButton("Config Block")
        optionButton.clicked.connect(lambda: self.show_option_panel())
        optionButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        blockLayout.addWidget(optionButton)

        # Button for adding the block to the pipeline
        addButton = QPushButton("Add")
        addButton.clicked.connect(lambda: add_block_callback(self))
        addButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        blockLayout.addWidget(addButton)

        return blockContainer
    
class Pass(ProcessBlock):
    def initialize(self):  
        self.info = {
            'name' : 'Base',
            'uuid' : None,
            'peaks' : False,
        }

        self.function = lambda signal: signal

class FIR(ProcessBlock):
    def initialize(self):  

        self.info = {
            'name' : 'FIR Filter',
            'uuid' : None,
            'extern': "TunerModule",
            'coefs': list(),
            'filter_options': {},
            'peaks' : False,
            'mode': 'Lowpass',
            'lower_corner': 20,
            'higher_corner': 40,
            'sampling_freq': 100,
            'attenuation': 0.7
        }

        #       Load Default coeffs
        def load_coeffs(file):
            values = list()
            with open(file, 'r') as f:
                for line in f:
                # Convert each line to a float and append to the list
                    coef = float(line.strip())
                    values.append(coef)  
            return values
        
        sampling_freq = 100
        # Coeffients depend on the frequency rate. Load the correct frequency coefficients.
        if sampling_freq == 500:
            coeffs = load_coeffs("./FIR_coefs/FIR_coefs_bandpass_500.csv")
        else:
            coeffs = load_coeffs("./FIR_coefs/FIR_coefs_bandpass_100.csv")
        
        self.info['coefs'] = coeffs

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
