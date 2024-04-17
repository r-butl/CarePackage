
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
        self.current_signal = []

    def add_process_block(self, process_block):
        """Adds a new process block to the pipeline"""
        newBlock = process_block
        newBlock.info['uuid'] = uuid.uuid4()    # Create a new uuid for the block

        # The block to the pipeline and set its next filter
        if self.pipeline_start == None:
            self.pipeline_start = newBlock
        else:
            # Find the end of the graph and append the block there
            curr = self.pipeline_start
            while curr != None:
                if curr.next_filter == None:
                    curr.next_filter = newBlock
                    break
                curr = curr.next_filter
        self.notify_observers()

    def print_pipeline(self):
        curr = self.pipeline_start

        while curr:
            print(curr.info['uuid'])
            curr = curr.next_filter

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

        self.notify_observers()

    def move_filter_up(self, id):
        """Move the Block up the pipeline"""

        # exit if the head node is the target, or if they don't exist
        if self.pipeline_start is None or self.pipeline_start.next_filter is None:
            return
        
        prev = None
        curr = self.pipeline_start

        # Node to swap is the second node in the list
        if curr.next_filter.info['uuid'] == id:
            second = self.pipeline_start.next_filter
            self.pipeline_start.next_filter = second.next_filter
            second.next_filter = self.pipeline_start
            self.pipeline_start = second
            self.notify_observers()
            return

        # Start on the second node
        prev = self.pipeline_start
        curr = self.pipeline_start.next_filter

        while curr and curr.next_filter:
            # iF the next node is our target, preform the swap
            if curr.next_filter.info['uuid'] == id:
                target = curr.next_filter
                curr.next_filter = target.next_filter
                target.next_filter = curr
                prev.next_filter = target
                self.notify_observers()
                return
            
            prev = curr
            curr = curr.next_filter

    def move_filter_down(self, id):
        
        # We need at least two blocks in the pipeline in order to work
        if self.pipeline_start is None or self.pipeline_start.next_filter is None:
            return
        
        prev = None
        curr = self.pipeline_start

        # Check if we are moving the head down
        if curr.info['uuid'] == id:
            target = self.pipeline_start
            self.pipeline_start = target.next_filter
            self.pipeline_start.next_filter = target
            target.next_filter = None
            self.notify_observers()
            return

        prev = self.pipeline_start
        curr = prev.next_filter

        while curr and curr.next_filter:
            # if the current node is our target perform the swap
            if curr.info['uuid'] == id:
                target = curr.next_filter
                curr.next_filter = target.next_filter
                target.next_filter = curr
                prev.next_filter = target
                self.notify_observers()
                return

            prev = curr
            curr = curr.next_filter

    def open_filter_settings(self, id):
        print("ACTION: Open option panel")
        
    def process_signal(self, signal):
        self.current_signal = signal
        if self.pipeline_start:
            self.pipeline_start.process(self.current_signal)   

    def set_observer(self, observer):
        self.observer = observer

    def notify_observers(self):
        self.process_signal(self.current_signal)

        if self.observer:
            self.observer.update()

#################################################################################

class PipelineController:
    def __init__ (self, option_viewer=None, pipeline_viewer=None, pipeline_model=None, update_view_callback=None):
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
        self.pipeline_viewer = pipeline_viewer

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

            # Add the element to the pipeline
            self.pipeline_model.add_process_block(newObject)
            

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
