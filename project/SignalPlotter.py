from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
    def __init__(self, parent=None, width=6, height=4, dpi=100):
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