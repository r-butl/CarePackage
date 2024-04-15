
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QSpinBox, QPushButton, QSizePolicy
import uuid
import copy
from ProcessBlocks import *
import CarePackage

#################################################################################

class PipelineModel:
    ''' The pipeline is a directed graph'''

    def __init__(self):
        self.pipeline_start = None
        self.blocks = []

    def add_process_block(self, process_block):
        """Adds a new process block to the pipeline"""
        new_block = process_block
        new_block.info['uuid'] = uuid.uuid4()    # Create a new uuid for the block

        # The block to the pipeline and set its next filter
        if self.pipeline_start == None:
            self.pipeline_start = new_block
        else:
            # Find the end of the graph and append the block there
            curr = self.pipeline_start
            while curr != None:
                if curr.next_filter == None:
                    curr.next_filter = new_block
                    break
                curr = curr.next_filter
        
        # Put it in the list
        self.blocks.append(new_block)

    def remove_by_id(self, id):
        ''' Remove an element by its ID'''
        curr = self.pipeline_start
        prev = None

        while curr is not None:
            if curr.info['uuid'] == id:
                # Check if this is the first block in the pipeline
                if prev == None:
                    self.pipeline_start = curr.next_filter
                else:
                    prev.next_filter = curr.next_filter
                
                del curr
                return
            else:
                prev = curr
                curr = curr.next_filter

    def move_filter_up(self, id):
        """Move the Block up the pipeline"""

        #       0 -> 1 -> 2
        #           1. Set 2 pointing to 1
        #       
        target = self.pipeline_start
        prev = None

        while curr is not None and curr.next_filter != None:
            if curr.next_filter.info['uuid'] == id:
                if prev == None:
                    # We are currently at the head of the pipeline
                    
                else:
                    if 

                return
            else:
                prev = curr
                curr = curr.next_filter

        
    def move_filter_down(self, id):
        index = 0
        for i in range(len(self.pipeline)):
            if self.pipeline[i]['uuid'] == id:
                index = i

        # Swap the elements:
        if len(self.pipeline) > 1 and index < len(self.pipeline) - 1:
            self.pipeline[index], self.pipeline[index + 1] = self.pipeline[index + 1], self.pipeline[index]
    
    def open_filter_settings(self, id):
        pass
        
    def process_signal(self, signalPlotController, signal):
        signalPlotController.reset_signals()
        signalPlotController.add_signal(signal, "Base Signal", [])
        for p in self.pipeline:
            signal = p.process(signal)
            signalPlotController.add_signal(signal, 
                                    p.get_info()['name'], 
                                    CarePackage.detect_peak(signal, 0.65) if p.get_info()['peaks'] else [])            

#################################################################################

class PipelineController:
    def __init__ (self, sampling_rate, option_viewer=None, pipeline_model=None, update_view_callback=None):
        self.starting_point = None

        self.info = [
            PS(),
            FIR(),
            CD(),
            MWI(),
            FPD(),
        ]

        self.pipeline_model = pipeline_model
        self.option_viewer = option_viewer

        self.update_view_callback = update_view_callback

        self.setup_UI()

    def setup_UI(self):
        '''Sets up the option panel'''
        for block in self.info:
            self.option_viewer.add_block_UI(block, self.update_option, self.option_panel_return_block_callback)

    def update_option(self, block, option, value):
        '''Used to update info in the process blocks'''
        if isinstance(block.info[option], bool):
            block.info[option] = bool(value)
        else:
            block.info[option] = value 

    def option_panel_return_block_callback(self, block):
        '''Gets a copy of the process block from the option panel and passes it to the pipeline'''
        if self.pipeline_model is not None:
            newObject = copy.deepcopy(block)
            self.pipeline_model.add_process_block(newObject)
        
        self.update_view_callback()

    def remove_by_id(self, id):
        self.pipeline_model.remove_by_id(id)
        self.update_view_callback()

    def move_filter_up(self, id):
        self.pipeline_model.remove_by_id(id)
        self.update_view_callback()

    def move_filter_down(self, id):
        self.pipeline_model.remove_by_id(id)
        self.update_view_callback()

    def open_filter_settings(self, id):
        self.pipeline_model.remove_by_id(id)
        self.update_view_callback()

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
        nameLabel = QLabel(block.info['name'])
        nameLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        blockLayout.addWidget(nameLabel)

        # Add the UI Element's modifyable properties
        for option, value in block.info.items():
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
