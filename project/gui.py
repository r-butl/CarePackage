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
                                QScrollArea
                                )

from SignalPlotter import *
from PTBXLsource import *
from PipelineConstructor import *

###########################################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CarePackage")
        self.setGeometry(100, 100, 1000, 10000)
        self.current_signal = None
        
        # Main layout
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # Top level layout
        topLevelLayout = QHBoxLayout(centralWidget)

        # Left and right panel
        leftPanelContainer = QWidget()
        leftPanel = QVBoxLayout(leftPanelContainer)

        rightPanelContainer = QWidget()
        rightPanel = QHBoxLayout(rightPanelContainer)

        ##################### Signal Plotter Sub Window

        self.signalPlotterGroup = QGroupBox("Signal Plotter")
        signalPlotterLayout = QVBoxLayout(self.signalPlotterGroup)

        self.signalView = SignalPlotView(self)
        self.signalModel = SignalPlotModel()
        self.signalController = SignalPlotController(self.signalModel, self.signalView)

        self.newSignalButton = QPushButton("New Signal", self)
        self.newSignalButton.clicked.connect( self.on_click_new_signal )
        
        signalPlotterLayout.addWidget(self.signalView)

        signalPlotterLayout.addWidget(self.newSignalButton)


        ##################### Data Base Sub Window

        self.sampling_options = [100, 500]
        self.sampling_options_index = 0
        self.path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/"

        self.dataControllerGroup = QGroupBox("Data Controller")
        dataControllerLayout = QVBoxLayout(self.dataControllerGroup)

        self.dataController = DataController(sampling_freq=self.sampling_options[self.sampling_options_index], path=self.path)

        # controlling the data
        self.sampleSelect = QComboBox()
        self.sampleSelect.addItems([ str(i) for i in self.sampling_options ])
        self.sampleSelect.currentIndexChanged.connect( lambda i: setattr(self, 'sampling_options_index', i) )

        self.sampleChange = QPushButton("Apply Changes", self)
        self.sampleChange.clicked.connect( self.apply_sample_change )

        ######

        dataControllerLayout.addWidget(QLabel("Select a Sampling Rate (hz):"))
        dataControllerLayout.addWidget(self.sampleSelect)
        dataControllerLayout.addWidget(self.sampleChange)


        ###################### Pipeline Construction Window

        self.pipelineControllerGroup = QGroupBox("Pipeline Constructor")
        pipelineControllerLayout = QVBoxLayout(self.pipelineControllerGroup)

        self.optionPanelViewer = OptionPanelViewer()
        self.pipelineModel = PipelineModel(self.update_signal_view)
        self.pipelineController = PipelineController(   sampling_rate=self.dataController.sampling_freq,  
                                                        option_viewer=self.optionPanelViewer, 
                                                        pipeline_viewer=None, 
                                                        pipeline_model=self.pipelineModel)
        
        pipelineControllerLayout.addWidget(self.optionPanelViewer)

        ####################

        
        leftPanel.addWidget(self.signalPlotterGroup, 6)
        leftPanel.addWidget(self.dataControllerGroup, 1)

        rightPanel.addWidget(self.pipelineControllerGroup)

        topLevelLayout.addWidget(leftPanelContainer,5)
        topLevelLayout.addWidget(rightPanelContainer,2)

    def on_click_new_signal(self):
        self.signalController.reset_signals()
        self.current_signal = self.dataController.give_signal()
        self.update_signal_view(self.current_signal)

    def update_signal_view(self, signal=None):
        if signal is None:
            signal = self.current_signal

        self.pipelineModel.process_signal(self.signalController, signal)
        self.signalView.plot_signals(self.signalModel)

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