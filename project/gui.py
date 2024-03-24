# Author: Lucas Butler

##########################################################################################

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import CarePackage
import dispatcher as d

##########################################################################################

class SignalPlotModel:
    def __init__(self):
        self.signals = []
        self.labels = []
        self.indices = []
        self.xlim = [0, 1000]

    def add_signal(self, signal=[], label="", indices=[]):
        if indices is None:
            indices = []
        self.signals.append(signal)
        self.labels.append(label)
        self.indices.append(indices)

    def reset(self):
        self.signals = []
        self.labels = []
        self.indices = []

class SignalPlotView(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(SignalPlotView, self).__init__(fig)
        self.setParent(parent)

    def plot_signals(self, model):
        self.figure.clf()
        signal_count = len(model.signals)
        if signal_count == 0:
            return
        
        self.axes_list = [self.figure.add_subplot(signal_count, 1, i + 1) for i in range(signal_count)]

        for i, (ax, signal) in enumerate(zip(self.axes_list, model.signals)):
            ax.plot(range(len(signal)), signal, label=model.labels[i])
            ax.set_xlim(model.xlim)
            for index in model.indices[i]:
                ax.axvline(x=index, color='r', linestyle='-')
            if model.labels[i]:
                ax.legend(loc='upper right')

        self.draw()

class SignalPlotController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_signal(self, signal, label="", indices=None):
        self.model.add_signal(signal, label, indices)

    def display_signals(self):
        self.view.plot_signals(self.model)

    def reset_signals(self):
        self.model.reset()

############################################################################################        

# Data controller 
class DataController:
    def __init__(self, sampling_freq=100):
        self.sampling_freq = sampling_freq
        self.data_source = d.data_dispatcher(path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/",
                                    sampling_rate=self.sampling_freq)

    def give_signal(self):
        return [i[0] for i in self.data_source.give_one_signal()[0].tolist()]
    
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
        self.databaseController = DataController(sampling_freq=sampling_freq)

        # Signal Pipeline
        self.pipelineController = PipelineController(self.databaseController.sampling_freq)

        # New Signal Button
        self.newSignalButton = QPushButton("New Signal", self)
        self.newSignalButton.clicked.connect(self.on_click_new_signal)

        layout.addWidget(self.newSignalButton)
        layout.addWidget(self.signalView)

        centralWidget.setLayout(layout)

    def on_click_new_signal(self):
        self.signalController.reset_signals()
        new_signal = self.databaseController.give_signal()
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