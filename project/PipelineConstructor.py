import CarePackage
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QSpinBox, QPushButton, QSizePolicy
import uuid
import copy

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

    def remove_next_filter(self):
        self.next_filter=None

class FIR(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : 'FIR Filter',
            'uuid' : None,
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
            'uuid' : None,
            'peaks' : False,
            'sampling_freq': 100
        }
    
    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.FPD(signal, self.options['sampling_freq'])

class PS(ProcessBlock):
    def __init__(self, next_filter=None):
        self.next_filter=next_filter
        self.options = {
            'name' : 'Pointwise Squaring',
            'uuid' : None,
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
            'uuid' : None,
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
            'uuid' : None,
            'peaks' : False,
            'sampling_freq' : 100
        }

    def process(self, signal):
        ''' Executes the process block'''
        return CarePackage.central_diff(signal, self.options['sampling_freq'])

#################################################################################

class OptionPanelViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = QWidget(self)

        self.layout = QVBoxLayout(self.container)

    def add_block_UI(self, block, update_option_callback, return_copy_callback):
        # Create a container for each block
        blockContainer = QWidget()
        blockLayout = QVBoxLayout(blockContainer)

        # Add a label
        nameLabel = QLabel(block.options['name'])
        nameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        blockLayout.addWidget(nameLabel)

        # Add the UI Element's modifyable properties
        for option, value in block.options.items():
            if option in ['name', 'uuid', 'sampling_freq']:
                continue
            
            self._add_option_widget(option, value, block, blockLayout, update_option_callback)

        # Apply style to customize appearance
        blockContainer.setStyleSheet("""
            QFrame {
                margin: 5px; 
            }
            QLabel {
                font-weight: bold;
            }
            QCheckBox, QSpinBox {
                background-color: #f0f0f0; 
            }
        """)
        
        # Button for adding the block to the pipeline
        addButton = QPushButton("Add")
        addButton.clicked.connect(lambda: return_copy_callback(block))
        addButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        blockLayout.addWidget(addButton)

        self.layout.addWidget(blockContainer)

    def _add_option_widget(self, option, value, block, layout, update_option_callback):

        optionWidget = None

        # Check what data type the option is and set it accordingly
        if isinstance(value, bool):
            optionWidget = QCheckBox()
            optionWidget.setChecked(value)
            optionWidget.stateChanged.connect(lambda state, opt=option, blk=block: update_option_callback(blk, opt, state))
        elif isinstance(value, (int, float)):
            optionWidget = QSpinBox()
            optionWidget.setValue(value)
            optionWidget.valueChanged.connect(lambda value, opt=option, blk=block: update_option_callback(blk, opt, value))

        # Create a container widget for the option
        optionContainer = QWidget()
        optionContainer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        optionLayout = QHBoxLayout(optionContainer)
        optionLabel = QLabel(option)
        optionLayout.addWidget(optionLabel)
        optionLayout.addWidget(optionWidget)

        # Add styles to customize appearance

        layout.addWidget(optionContainer)

############################################################################

class PipelineController:
    def __init__ (self, sampling_rate, option_viewer=None, pipeline_viewer=None, pipeline_model=None, update_view_callback=None):
        self.starting_point = None

        self.options = [
            PS(),
            FIR(),
            CD(),
            MWI(),
            FPD(),
        ]

        self.pipeline_model = pipeline_model
        self.pipeline_viewer = pipeline_viewer
        self.option_viewer = option_viewer

        self.update_view_callback = update_view_callback

        self.setup_UI()

    def setup_UI(self):
        '''Sets up the option panel and the pipeline viewer'''
        for block in self.options:
            self.option_viewer.add_block_UI(block, self.update_option, self.option_panel_return_block_callback)

    def update_option(self, block, option, value):
        '''Used to update options in the process blocks'''
        if isinstance(block.options[option], bool):
            block.options[option] = bool(value)
        else:
            block.options[option] = value 

    def option_panel_return_block_callback(self, block):
        '''Gets a copy of the process block from the option panel and passes it to the pipeline'''
        if self.pipeline_model is not None:
            newObject = copy.deepcopy(block)
            self.pipeline_model.add_process_block(newObject)
        
        self.update_view_callback()

    def remove_last_filter(self):
        self.pipeline_model.remove_process_block()

        self.update_view_callback()
    
class PipelineModel:
    def __init__(self):
        self.pipeline = []

    def add_process_block(self, process_block):
        """Adds a new process block to the pipeline"""
        new_block = process_block
        new_block.options['uuid'] = uuid.uuid4()    # Create a new uuid for the block

        # The block to the pipeline and set its next filter
        if self.pipeline:
            self.pipeline[-1].set_next_filter(new_block)
        
        self.pipeline.append(process_block)

    def remove_process_block(self):
        '''Removes the latest signal processing block'''
        if len(self.pipeline) > 0:
            del self.pipeline[-1]       # Remove the last process block

        if len(self.pipeline) > 0:
            self.pipeline[-1].remove_next_filter()  # Remove the next filter pointer from the last process block
        
    def process_signal(self, signalPlotController, signal):
        signalPlotController.reset_signals()
        signalPlotController.add_signal(signal, "Base Signal", [])
        for p in self.pipeline:
            signal = p.process(signal)
            signalPlotController.add_signal(signal, 
                                    p.get_options()['name'], 
                                    CarePackage.detect_peak(signal, 0.65) if p.get_options()['peaks'] else [])            

class PipelineViewer(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.pipelineDisplay = QLabel("Pipeline Configuration")
        self.layout.addWidget(self.pipelineDisplay)
