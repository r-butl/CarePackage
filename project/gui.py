# Author: Lucas Butler

##########################################################################################

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

import CarePackage
from SignalPlotter import *
from PTBXLsource import *


###########################################################################################


class FunctionBlockModel:
    def __init__(self):
        self.function = None
        self.options = []

class PipelineController:
    def __init__(self, sampling_freq):
        self.sampling_freq = sampling_freq
        pass

    def process_signal(self, controller, signal):
        controller.add_signal(signal, "Original Signal", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.FIR(signal)
        controller.add_signal(signal, "FIR", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.fivepoint_diff(signal, self.sampling_freq)
        controller.add_signal(signal, "Five Point Differential", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.pointwise_squaring(signal)
        controller.add_signal(signal, "Pointwise Squaring", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.moving_window_integration(signal, 20)
        controller.add_signal(signal, "Moving Window Integration", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.central_diff(signal, self.sampling_freq)
        controller.add_signal(signal, "Central Differential", CarePackage.detect_peak(signal, 0.65))


###########################################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pipeline View")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        
        # Use QVBoxLayout for the central widget
        layout = QVBoxLayout(centralWidget)

        # Signal Plotter
        self.signalView = SignalPlotView(self)
        self.signalModel = SignalPlotModel()
        self.signalController = SignalPlotController(self.signalModel, self.signalView)

        # Data base
        sampling_freq = 100
        path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/"
        self.dataController = DataController(sampling_freq=sampling_freq, path=path)

        # Signal Pipeline
        self.pipelineController = PipelineController(self.dataController.sampling_freq)

        # New Signal Button
        self.newSignalButton = QPushButton("New Signal", self)
        self.newSignalButton.clicked.connect(self.on_click_new_signal)

        layout.addWidget(self.newSignalButton)
        layout.addWidget(self.signalView)

        centralWidget.setLayout(layout)

    def on_click_new_signal(self):
        self.signalController.reset_signals()
        new_signal = self.dataController.give_signal()
        self.pipelineController.process_signal(self.signalController, new_signal)
        self.signalView.plot_signals(self.signalModel)
    
def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()  # Temporarily pass None for the controller

    mainWindow.on_click_new_signal()
    mainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()