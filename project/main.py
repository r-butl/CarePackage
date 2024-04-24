# Author: Lucas Butler

##########################################################################################

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import     (
                                QApplication, 
                                QMainWindow, 
                                QVBoxLayout, 
                                QHBoxLayout,
                                QWidget, 
                                QPushButton, 
                                QGroupBox,
                                QComboBox,
                                QLabel,
                                )

from SignalPlotter import *
from PTBXLsource import *
from PipelineConstructor import *
from TopBar import *

###########################################################################################

class MainWindow(QMainWindow):
    def __init__(self, exit_callback=None):
        super().__init__()

        self.setWindowTitle("CarePackage")
        self.setGeometry(100, 50, 1500, 1000)
        
        self.sampling_options = [100, 500]
        self.sampling_options_index = 0
        self.path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/"

        ##################################################### Central Layout

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        topLevelLayout = QVBoxLayout(centralWidget)
        
        topBarContainer = TopMenuBar(exit_callback=exit_callback)

        functionalViewWidget = QWidget()
        functionalViewLayout = QHBoxLayout(functionalViewWidget)

        leftPanelContainer = QWidget()
        leftPanel = QVBoxLayout(leftPanelContainer)

        rightPanelContainer = QWidget()
        rightPanel = QVBoxLayout(rightPanelContainer)
          
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)

        ##################################################### Data Base 

        self.dataController = DataController(           sampling_freq=self.sampling_options[self.sampling_options_index], 
                                                        path=self.path)
        
        ################################################################ Pipeline Construction 
        
        self.pipelineModel = PipelineModel()

        self.optionPanelViewer = OptionPanelViewer()
        self.pipelineViewer = PipelineViewer(           model = self.pipelineModel,
                                                        sampling_freq=self.sampling_options[self.sampling_options_index])
        
        self.pipelineController = PipelineController(   option_viewer=self.optionPanelViewer,
                                                        pipeline_viewer=self.pipelineViewer, 
                                                        pipeline_model=self.pipelineModel)
        self.on_click_new_signal()
        self.pipelineController.add_base_block()
        self.pipelineController.update_latest_signal(self.pipelineModel.current_signal)
        self.pipelineController.setup_UI()

        self.pipelineGroup = QGroupBox("Pipeline Viewer")
        pipelineLayout = QVBoxLayout(self.pipelineGroup)
        pipelineLayout.addWidget(self.pipelineViewer)

        self.controlPanelGroup = QGroupBox("Control Panel")
        controlPanelLayout = QVBoxLayout(self.controlPanelGroup)

        # Select Sample rate
        self.sampleSelect = QComboBox()
        self.sampleSelect.addItems([ str(i) for i in self.sampling_options ])
        self.sampleSelect.currentIndexChanged.connect( lambda i: setattr(self, 'sampling_options_index', i) )

        # Apply Sample rate changes
        self.sampleChange = QPushButton("Apply Changes", self)
        self.sampleChange.clicked.connect( self.apply_sample_change )

        # New Signal Button
        self.newSignalButton = QPushButton("New Signal", self)
        self.newSignalButton.clicked.connect(self.on_click_new_signal)

        self.toggleRealtimeButton = QPushButton("Toggle Real Time Simulator", self)
        self.toggleRealtimeButton.clicked.connect(self.pipelineViewer.toggle_masks)

        controlPanelLayout.addWidget(QLabel("Select a Sampling Rate (hz):"))
        controlPanelLayout.addWidget(self.sampleSelect)
        controlPanelLayout.addWidget(self.sampleChange)
        controlPanelLayout.addWidget(self.newSignalButton)
        controlPanelLayout.addWidget(self.toggleRealtimeButton)
        ############################# Right Panel

        rightPanel.addWidget(self.pipelineGroup)
        rightPanel.addWidget(self.controlPanelGroup)

        ############################# Option Panel Viewer

        self.optionPanelGroup = QGroupBox("Process Block Options")
        optionPanelLayout = QVBoxLayout(self.optionPanelGroup)

        optionPanelLayout.addWidget(self.optionPanelViewer)
        
        #########################   Left Panel

        leftPanel.addWidget(self.optionPanelGroup)

        # Functional Panel
        functionalViewLayout.addWidget(leftPanelContainer,1)
        functionalViewLayout.addWidget(rightPanelContainer, 4)

        # Top Level
        topLevelLayout.addWidget(topBarContainer)
        topLevelLayout.addWidget(functionalViewWidget)

    def on_click_new_signal(self):
        print("on click new signal")
        self.pipelineModel.current_signal = self.dataController.give_signal()
        self.update_signal_view(self.pipelineModel.current_signal)

    def update_signal_view(self, signal=None):
        print("update signal view")
        if signal is None:
            signal = self.pipelineModel.current_signal
        self.pipelineController.process_signal(signal)

    def apply_sample_change(self):
        print("apply sample change")
        self.dataController = DataController(sampling_freq=self.sampling_options[self.sampling_options_index], path=self.path)    # Reload the dataabase
        self.pipelineController.update_sampling_freq(self.sampling_options[self.sampling_options_index])
        self.on_click_new_signal()

def main():

    app = QApplication(sys.argv)
    mainWindow = MainWindow(exit_callback=app.quit)  # Temporarily pass None for the controller

    mainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()