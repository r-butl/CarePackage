from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea, QSizePolicy, QSpacerItem, QHBoxLayout, QPushButton

class IndividualPlotView(FigureCanvas):
    def __init__(self, parent, width=6, height=2, dpi=100, signal=None, label="", indices=[], xlim=[0, 1000], controller=None, id=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)           
        super().__init__(self.fig)
        self.setParent(parent)
        self.controller = controller
        self.block_id = id

        self.axes = self.fig.add_subplot(111)
        if signal:
            self.axes.plot(range(len(signal)), signal, label=label)
            self.axes.set_xlim(xlim)
            for index in indices:
                self.axes.axvline(x=index, color='r', linestyle='-')
            if label:
                self.axes.set_title(label)

        # Set a fixed height for the plot
        self.setFixedHeight(height * dpi)

        self.init_controls()

    def init_controls(self):
        layout = QHBoxLayout()
        move_up_button = QPushButton("Move Up")
        move_up_button.clicked.connect(self.move_up)
        move_down_button = QPushButton("Move Down")
        move_down_button.clicked.connect(self.move_down)
        remove = QPushButton("Remove")
        remove.clicked.connect(self.remove_filter)
        options = QPushButton("Options")
        options.clicked.connect(self.open_settings)

        layout.addWidget(move_up_button)
        layout.addWidget(move_down_button)
        layout.addWidget(remove)
        layout.addWidget(options)

        self.layout().addLayout(layout)

    def move_up(self):
        if self.controller:
            self.controller.move_filter_up(self.block_id)

    def move_down(self):
        if self.controller:
            self.controller.move_filter_down(self.block_id)
    
    def remove_filter(self):
        if self.controller:
            self.controller.remove_by_id(self.block_id)

    def open_settings(self):
        if self.controller:
            self.controller.open_filter_settings(self.block_id)

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
    def __init__(self, model, pipeline_controller, parent=None):
        super().__init__(parent)
        self.model = model
        self.pipeline_controller = pipeline_controller

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
        individual_signal_container = QWidget()
        individual_signal_layout = QHBoxLayout(individual_signal_container)

        # Create individual plots for each signal
        for i in range(len(self.model.signals)):
            plotView = IndividualPlotView(parent=None,  signal=self.model.signals[i],
                                          label=self.model.labels[i], indices=self.model.indices[i],
                                          xlim=self.model.xlim, controller=self.pipeline_controller )
            
            individual_signal_layout.addWidget(plotView)
            
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