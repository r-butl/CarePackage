from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QSizePolicy, QSpacerItem

class IndividualPlotView(FigureCanvas):
    def __init__(self, parent, width=6, height=2, dpi=100, signal=None, label="", indices=[], xlim=[0, 1000]):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        if signal is not None:
            self.axes.plot(range(len(signal)), signal, label=label)
            self.axes.set_xlim(xlim)
            for index in indices:
                self.axes.axvline(x=index, color='r', linestyle='-')
            if label:
                self.axes.set_title(label)
        super().__init__(fig)
        self.setParent(parent)

        # Set a fixed height for the plot
        pixelsPerInch = dpi
        fixedHeightInPixels = height * pixelsPerInch
        self.setFixedHeight(fixedHeightInPixels)

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

class SignalPlotView(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model

        self.initUI()
        self.display_signals()

    def initUI(self):
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # Container for the plots
        self.plotContainerWidget = QWidget()
        self.plotLayout = QVBoxLayout(self.plotContainerWidget)
        self.scrollArea.setWidget(self.plotContainerWidget)

        # Main layout for this widget to include the scroll area
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.scrollArea)
        self.setLayout(mainLayout)

        # Set the size policy to make the widget expanding
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        # Ensure the scroll area expands fully within SignalPlotView
        self.scrollArea.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)   # take the first item in the layout
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                # Recursively clear any nested layouts
                nestedLayout = item.layout()
                if nestedLayout:
                    self.clearLayout(nestedLayout)
                # Remove spacer items or other non-widget items
                else:
                    del item
    
    def display_signals(self):
        
        self.clearLayout(self.plotLayout)

        # Create individual plots for each signal
        for i in range(len(self.model.signals)):
            plotView = IndividualPlotView(parent=None,  signal=self.model.signals[i],
                                          label=self.model.labels[i], indices=self.model.indices[i],
                                          xlim=self.model.xlim)
            self.plotLayout.addWidget(plotView)
        
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.plotLayout.addSpacerItem(spacer)


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