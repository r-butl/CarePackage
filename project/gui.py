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
                                QLabel
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
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)




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

        self.sampleSelect = QComboBox()
        self.sampleSelect.addItems([ str(i) for i in self.sampling_options ])
        self.sampleSelect.currentIndexChanged.connect( self.update_sampling_rate )
        self.sampleChange = QPushButton("Apply Changes", self)
        self.sampleChange.clicked.connect( self.applySampleChange )

        dataControllerLayout.addWidget(QLabel("Select a Sampling Rate (hz):"))
        dataControllerLayout.addWidget(self.sampleSelect)
        dataControllerLayout.addWidget(self.sampleChange)


        ###################### Pipeline Construction Window

        self.pipelineController = PipelineController(self.dataController.sampling_freq)


        ####################

        
        mainLayout.addWidget(self.signalPlotterGroup, 4)
        mainLayout.addWidget(self.dataControllerGroup, 1)
        centralWidget.setLayout(mainLayout)



    def on_click_new_signal(self):
        self.signalController.reset_signals()
        new_signal = self.dataController.give_signal()
        self.pipelineController.process_signal(self.signalController, new_signal)
        self.signalView.plot_signals(self.signalModel)

    def update_sampling_rate(self, i):
        self.sampling_options_index = i

    def applySampleChange(self):
        self.pipelineController.update_sampling_rate(self.sampling_options[self.sampling_options_index])  # Reconfigure the pipeline
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