
from PyQt5.QtWidgets import (   QWidget, 
                                QVBoxLayout, 
                                QSizePolicy,
                                QScrollArea
                            )
import uuid
import copy
from ProcessBlocks import *

#################################################################################

class PipelineModel:
    ''' The pipeline is a directed graph'''

    def __init__(self):
        self.pipeline_start = None
        self.pipeline_end = None
        self.current_signal = []

    def print_pipeline(self):
        curr = self.pipeline_start

        while curr:
            print(curr.info['uuid'])
            curr = curr.next_filter

    def set_pipeline_end(self):
        """Sets the end of the pipeline to the last node in the graph"""
        curr = self.pipeline_start

        # Base Case
        if curr.next_filter == None:
            self.pipeline_end = curr

        while curr:
            if curr.next_filter == None:
                self.pipeline_end = curr
                return
            else:
                curr = curr.next_filter

    def add_process_block(self, process_block):
        """Adds a new process block to the pipeline"""
        newBlock = process_block
        newBlock.parent = self
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
        
        self.set_pipeline_end()
        self.notify_observers()

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
                self.notify_observers()
                break
            else:
                prev = curr
                curr = curr.next_filter

        self.set_pipeline_end()

    def move_filter_up(self, id):
        """Move the Block up the pipeline"""

        # exit if the head node is the target, or if they don't exist
        if self.pipeline_start is None or self.pipeline_start.next_filter is None:
            return
        
        prev = None
        curr = self.pipeline_start

        # Node to swap is the second node in the list
        if curr.next_filter.info['uuid'] == id and curr.info['name'] != 'Base':
            second = self.pipeline_start.next_filter
            self.pipeline_start.next_filter = second.next_filter
            second.next_filter = self.pipeline_start
            self.pipeline_start = second
            self.set_pipeline_end()
            self.notify_observers()
            return

        # Start on the second node
        prev = self.pipeline_start
        curr = self.pipeline_start.next_filter

        while curr and curr.next_filter:
            # Ensure that we are not trying to swap the base signal
            # iF the next node is our target, preform the swap
            if curr.next_filter.info['uuid'] == id :
                target = curr.next_filter
                curr.next_filter = target.next_filter
                target.next_filter = curr
                prev.next_filter = target
                self.set_pipeline_end()
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
            head = self.pipeline_start
            next = self.pipeline_start.next_filter

            head.next_filter = next.next_filter
            next.next_filter = head
            self.pipeline_start = next
            self.set_pipeline_end()
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
                self.set_pipeline_end()
                self.notify_observers()
                return

            prev = curr
            curr = curr.next_filter

    def open_filter_settings(self, id):
        curr = self.pipeline_start

        while curr:
            if curr.info["uuid"] == id:
                curr.show_option_panel() 

            curr = curr.next_filter    

    def process_signal(self, signal=None):
        if signal != None:
            self.current_signal = signal

        if self.pipeline_start:
            self.pipeline_start.process(self.current_signal)   

    def set_observer(self, observer):
        self.observer = observer

    def notify_observers(self):
        self.process_signal(self.current_signal)
        if self.observer:
            self.observer.update_signal()

    def update_sampling_freq(self, sampling_freq):
        curr = self.pipeline_start

        while curr:
            curr.update_info('sampling_freq', sampling_freq)
            curr = curr.next_filter

#################################################################################

class PipelineController:

    def __init__ (self, option_viewer=None, pipeline_viewer=None, pipeline_model=None):
        self.starting_point = None

        self.options = [
            PS(),
            FIR(),
            CD(),
            MWI(),
            FPD(),
        ]

        self.pipeline_model = pipeline_model
        self.option_viewer = option_viewer
        self.pipeline_viewer = pipeline_viewer

    def update_sampling_freq(self, sampling_freq):
        for o in self.options:
            o.update_info('sampling_freq', sampling_freq)

        self.pipeline_model.update_sampling_freq(sampling_freq)

    def add_base_block(self):
        '''create a Buffer block and Add it to the pipeline'''
        baseBlock = Pass()
        self.option_panel_return_block_callback(baseBlock)

    def setup_UI(self):
        '''Sets up the option panel'''
        for block in self.options:
            self.option_viewer.add_block_UI(block, self.option_panel_return_block_callback)

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
            self.update_latest_signal(self.pipeline_model.pipeline_end.signal_prev_stage if self.pipeline_model.pipeline_end.signal_prev_stage else self.pipeline_model.pipeline_end.signal)

    def update_latest_signal(self, signal=None):
        """Updates each of the process block options with a signal when we access them in the options panel,
        it displays the latest signal in the pipeline"""
        for opt in self.options:
            opt.signal = signal

    def process_signal(self, signal):
        """Sends a new signal to through the pipeline"""
        self.pipeline_model.process_signal(signal)
        if self.pipeline_model.pipeline_end:
            self.update_latest_signal(self.pipeline_model.pipeline_end.signal_prev_stage if self.pipeline_model.pipeline_end.signal_prev_stage else self.pipeline_model.pipeline_end.signal)
            
#################################################################################

class OptionPanelViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.container = QWidget(self)

        self.layout = QVBoxLayout(self.container)
        self.init_UI()

    def init_UI(self):
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        # Container for the options
        self.optionContainerWidget = QWidget()
        self.optionLayout = QVBoxLayout(self.optionContainerWidget)
        self.scrollArea.setWidget(self.optionContainerWidget)

        # Main layout for the option panel
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.scrollArea)
        self.setLayout(mainLayout)

        # Set the Size Policy
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.scrollArea.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def clear_UI(self):
        """Clears the UI"""

    def add_block_UI(self, block, return_copy_callback):
        """Adds a process block to the options panel"""
        # Create a container for each block
        blockUI = block.create_option_ui(return_copy_callback)
        self.optionLayout.addWidget(blockUI)

