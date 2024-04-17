from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QVBoxLayout, 
                             QWidget, 
                             QScrollArea, 
                             QSizePolicy, 
                             QSpacerItem, 
                             QHBoxLayout, 
                             QPushButton)

class IndividualPlotView(FigureCanvas):
    def __init__(self, parent, width=6, height=2, dpi=100, signal=None, label="", indices=[], xlim=[0, 1000], controller=None, id=None):
        self.fig = Figure(figsize=(width, height), dpi=dpi)           
        super().__init__(self.fig)
        self.setParent(parent)
        self.controller = controller
        self.block_id = id

        self.axes = self.fig.add_subplot(111)
        self.line = None    # Plot line
        self.indicies_lines = []    # lines of indicies
        self.initialize_plot(signal, label, indices, xlim)

        # Set a fixed height for the plot
        self.setFixedHeight(height * dpi)

        self.init_controls()

    def initialize_plot(self, signal, label, indices, xlim):
        """Initial the plot"""
        if signal:
            self.line, = self.axes.plot(range(len(signal)), signal, label=label)
            self.axes.set_xlim(xlim)
            for index in indices:
                line = self.axes.axvline(x=index, color='r', linestyle='-')
                self.indicies_lines.append(line)    # Store each vertical line
            if label:
                self.axes.set_title(label)

    def update_signal(self, new_signal, new_indices=None):
        """Update the plot with the new signal"""
        if self.line is not None:
            self.line.set_ydata(new_signal)
            self.line.set_xdata(range(len(new_signal)))
                                
        if new_indices is not None:
            # Remove old indicies
            for line in self.indices_lines:
                line.remove()
            self.indicies_lines.clear()

            # Add new indices
            for index in new_indices:
                line = self.axes.axvline(x=index, color='r', linestyle='-')
                self.indicies_lines.append(line)

        self.fig.canvas.draw_idle()     # redraw the plot

    def init_controls(self):
        """If related to a process block, then  add controls, otherwise don't"""
        if self.controller:
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

class PipelineViewer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

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

    def add_element(self, new_element):
        
    
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


