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
                             QSpinBox,
                             QCheckBox,
                             QLabel,
                             QDialog,
                             QDialogButtonBox
                             )

class ProcessBlock(ABC):

    def __init__(self, next_filter=None, observer=None, peaks = False):
        self.info = {}  
        self.next_filter = None
        self.observers = []
        self.function = None
        self.signal = []
        self.signal_prev_stage = []
        self.indicies = []
        self.initialize()

    @abstractmethod
    def initialize(self):
        """ Initialize subclass specific settings like function and info. """
        pass

    def process(self, signal=None):
        ''' Executes the process block'''
        if signal != None:
            self.signal_prev_stage = signal

        if self.signal_prev_stage or self.signal:
            if self.function:
                self.signal = self.function(self.signal_prev_stage)

            if self.info['peaks'] == True:
                self.indicies = CarePackage.detect_peak(self.signal, 75)
                print(self.indicies)
            else:
                self.indicies = []

            # Send the signal information to the plots that are observing the process block
            for observer in self.observers:
                observer.update_signal(self.signal, self.indicies)

            if self.next_filter:
                self.next_filter.process(self.signal)
                
    def set_info(self, option, value):
        ''' Sets the configurable parameters of the process block'''
        if option in self.info and type(value) == type(self.info[option]):
            self.info[option] = value

    def set_next_filter(self, filter):
        self.next_filter = filter

    def remove_next_filter(self):
        self.next_filter=None

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
            else:
                print("ERROR: Process Block - Mismatch value for option")
        else:
            print("ERROR: Process Block - Option not in info panel.")
        
        self.process()

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

        blockContainer.setStyleSheet("""
            QFrame {
                margin: 5px; 
            }

            QCheckBox, QSpinBox {
                background-color: #f0f0f0; 
            }
        """)

        return blockContainer

    def show_option_panel(self):
        """ Defines a popup window for the options panel"""

        dialog = QDialog()
        dialog.setWindowTitle("Configuration Options")

        layout = QVBoxLayout(dialog)

        for option, value in self.info.items():
            if option in ['name', 'uuid', 'sampling_freq']:
                continue
            optionWidget = self._create_option_widget(option, value)
            layout.addWidget(optionWidget)

        dialog.setStyleSheet("""
            QFrame {
                margin: 5px; 
            }

            QCheckBox, QSpinBox {
                background-c~olor: #f0f0f0; 
            }
        """)

        applyButton = QDialogButtonBox(QDialogButtonBox.Apply)
        applyButton.button(QDialogButtonBox.Apply).clicked.connect(dialog.accept) 
        layout.addWidget(applyButton)

        dialog.exec_()

    def _create_option_widget(self, option, value):

        optionWidget = None

        # Check what data type the option is and set it accordingly
        if isinstance(value, bool):
            optionWidget = QCheckBox()
            optionWidget.setChecked(value)
            optionWidget.stateChanged.connect(lambda state, opt=option: self.update_info(opt, bool(state)))
        elif isinstance(value, (int, float)):
            optionWidget = QSpinBox()
            optionWidget.setValue(value)
            optionWidget.valueChanged.connect(lambda value, opt=option: self.update_info(opt, value))

        # Create a container widget for the option
        optionContainer = QWidget()
        optionContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        optionLayout = QHBoxLayout(optionContainer)
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
            'peaks' : False,
            'sampling_freq' : 100,
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
