# Author: Lucas Butler

##########################################################################################

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import     (QApplication, 
                                QMainWindow, 
                                QVBoxLayout, 
                                QHBoxLayout,
                                QWidget, 
                                QPushButton, 
                                QGroupBox,
                                QComboBox,
                                QLabel,
                                QSizePolicy
                                )

from SignalPlotter import *
from PTBXLsource import *
from PipelineConstructor import *

###########################################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CarePackage")
        self.setGeometry(100, 50, 1500, 1000)
        self.current_signal = None
        
        ################################################## MVC defintions

        ###  Data Base 

        self.sampling_options = [100, 500]
        self.sampling_options_index = 0
        self.path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/"

        self.dataController = DataController(           sampling_freq=self.sampling_options[self.sampling_options_index], 
                                                        path=self.path)

        ### Pipeline Construction 

        self.optionPanelViewer = OptionPanelViewer()
        self.pipelineModel = PipelineModel()
        self.pipelineController = PipelineController(   sampling_rate=self.dataController.sampling_freq,  
                                                        option_viewer=self.optionPanelViewer, 
                                                        pipeline_viewer=None, 
                                                        pipeline_model=self.pipelineModel,
                                                        update_view_callback=self.update_signal_view)
        
        ### Signal Plotter

        self.signalModel = SignalPlotModel()
        self.signalView = SignalPlotView(               model=self.signalModel)
        self.signalController = SignalPlotController(   model=self.signalModel, 
                                                        view=self.signalView)
        
        ################################################# Utilities Definition

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

        # Remove Latest Filter Button
        self.removeFilterButton = QPushButton("Remove Last Filter", self)
        self.removeFilterButton.clicked.connect(self.pipelineController.remove_last_filter)

        ##################################################### 

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        topLevelLayout = QHBoxLayout(centralWidget)

        leftPanelContainer = QWidget()

        leftPanel = QVBoxLayout(leftPanelContainer)

        centerPanelContainer = QWidget()

        centerPanel = QVBoxLayout(centerPanelContainer)

        rightPanelContainer = QWidget()
        rightPanel = QVBoxLayout(rightPanelContainer)


        self.controlPanelGroup = QGroupBox("Control Panel")
        controlPanelLayout = QVBoxLayout(self.controlPanelGroup)



        #####################################################  Layout

        # Left Panel
        leftPanel.addWidget(self.optionPanelViewer)
        leftPanel.addWidget(self.removeFilterButton)

        # Center Panel
        centerPanel.addWidget(self.signalView)

        controlPanelLayout.addWidget(QLabel("Select a Sampling Rate (hz):"))
        controlPanelLayout.addWidget(self.sampleSelect)
        controlPanelLayout.addWidget(self.sampleChange)
        controlPanelLayout.addWidget(self.newSignalButton)

        centerPanel.addWidget(self.controlPanelGroup)


        # All together now
        topLevelLayout.addWidget(leftPanelContainer,1)
        topLevelLayout.addWidget(centerPanelContainer, 4)

    def on_click_new_signal(self):
        self.signalController.reset_signals()
        self.current_signal = self.dataController.give_signal()
        self.update_signal_view(self.current_signal)

    def update_signal_view(self, signal=None):
        if signal is None:
            signal = self.current_signal

        self.pipelineModel.process_signal(self.signalController, signal)
        self.signalView.display_signals()

    def apply_sample_change(self):
        #self.pipelineController.update_sampling_rate(self.sampling_options[self.sampling_options_index])  # Reconfigure the pipeline
        self.dataController = DataController(sampling_freq=self.sampling_options[self.sampling_options_index], path=self.path)    # Reload the dataabase
        self.on_click_new_signal()


def main():

    app = QApplication(sys.argv)
    mainWindow = MainWindow()  # Temporarily pass None for the controller

    mainWindow.on_click_new_signal()
    mainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()