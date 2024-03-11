import dispatcher as d
from matplotlib import pyplot as plt
import CarePackage

def plot_signals(signals, xlim, labels, indices):
    if type(signals) != list:
        print("argument must be in list format")
        return
    
    for i in range(len(signals)):
        ax = plt.subplot(len(signals), 1, i+1)  # Two rows, one column, first plot
        ax.plot([j for j in range(len(signals[i]))], signals[i])
        ax.set_xlim([0, xlim])

        if len(labels) == len(signals):
            bbox = ax.get_position()
            x = bbox.x0 + bbox.width / 2  # Center of subplot horizontally
            y = bbox.y1  # Top of subplot vertically
            plt.figtext(x, y-0.005, labels[i], ha='center', va='top')  # Place label on top   
            
        if i == len(signals) - 1:  # Check if it's the last signal plot
            for index in indices:
                ax.axvline(x=index, color='r', linestyle='-')  # Plot vertical line
    
    plt.show()

def pipeline(signals: list):
        # Apply FIR filter
    signals.append(CarePackage.FIR(signals[-1]))
    signals.append(CarePackage.fivepoint_diff(signals[-1], sampling_freq))
    signals.append(CarePackage.pointwise_squaring(signals[-2]))
    signals.append(CarePackage.moving_window_integration(signals[-1]))
    signals.append(CarePackage.central_diff(signals[-1], sampling_freq))
    return signals


if __name__ == "__main__":

    sampling_freq = 100
    data_source = d.data_dispatcher(path="/home/lucas/Desktop/programming/classwork/Senior_project/project/data/",
                                    sampling_rate=sampling_freq)

    # Look at some signals
    signals = list()
    for i in range(4): signals.append([i[0] for i in data_source.give_one_signal()[0].tolist()])
    #plot_signals(signals)

    # Apply pipeline to one
    signals = list()
    signals.append([i[0] for i in data_source.give_one_signal()[0].tolist()])
    signals = pipeline(signals)
    indices = CarePackage.detect_QRS(signals[-1])

    length_limit = 1000
    labels = ["Original", "FIR", "Five-point Differential", "Pointwise Squaring", "Moving Window Integration", "Detect_QRS"]
    plot_signals(signals, length_limit, labels, indices)

    