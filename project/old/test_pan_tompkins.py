import dispatcher as d
from matplotlib import pyplot as plt
import CarePackage

class SignalModel:
    def __init__(self):
        self.signals = []
        self.labels = []
        self.indices = []
        self.xlim = [0, 1000]

    def add_signal(self, signal, label="", indices=None):
        if indices is None:
            indices = []
        self.signals.append(signal)
        self.labels.append(label)
        self.indices.extend(indices)

class SignalView:
    @staticmethod
    def plot_signals(model):
        for i, signal in enumerate(model.signals):
            ax = plt.subplot(len(model.signals), 1, i + 1)
            ax.plot([j for j in range(len(signal))], signal)
            ax.set_xlim(model.xlim)

            if len(model.labels) == len(model.signals):
                bbox = ax.get_position()
                x = bbox.x0 + bbox.width / 2  # Center of subplot horizontally
                y = bbox.y1  # Top of subplot vertically
                plt.figtext(x, y - 0.005, model.labels[i], ha='center', va='top')  # Place label on top

            if i == len(model.signals) - 1:  # Check if it's the last signal plot
                for index in model.indices:
                    ax.axvline(x=index, color='r', linestyle='-')  # Plot vertical line

        plt.show()

class SignalController:
    def __init__(self):
        self.model = SignalModel()
        self.view = SignalView()

    def add_signal(self, signal, label="", indices=None):
        self.model.add_signal(signal, label, indices)

    def display_signals(self):
        self.view.plot_signals(self.model)


def pipeline(signals: list):
        # Apply FIR filter
    signals.append(CarePackage.FIR(signals[-1]))
    signals.append(CarePackage.fivepoint_diff(signals[-1], sampling_freq))
    signals.append(CarePackage.pointwise_squaring(signals[-2]))
    signals.append(CarePackage.moving_window_integration(signals[-1], 20))
    signals.append(CarePackage.central_diff(signals[-1], sampling_freq))
    return signals


if __name__ == "__main__":

    sampling_freq = 100
    data_source = d.data_dispatcher(path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/",
                                    sampling_rate=sampling_freq)
    controller = SignalController()

    # Look at some signals
    while True:

        signal = [i[0] for i in data_source.give_one_signal()[0].tolist()]
        controller.add_signal(signal, "Original Signal", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.FIR(signal)
        controller.add_signal(signal, "FIR", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.fivepoint_diff(signal, sampling_freq)
        controller.add_signal(signal, "Five Point Differential", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.pointwise_squaring(signal)
        controller.add_signal(signal, "Pointwise Squaring", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.moving_window_integration(signal, 20)
        controller.add_signal(signal, "Moving Window Integration", CarePackage.detect_peak(signal, 0.65))

        signal = CarePackage.central_diff(signal, sampling_freq)
        controller.add_signal(signal, "Central Differential", CarePackage.detect_peak(signal, 065))

        controller.display_signals()

    