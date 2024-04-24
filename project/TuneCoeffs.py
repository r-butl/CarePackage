from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas # type: ignore
from matplotlib.figure import Figure # type: ignore
from PyQt5.QtWidgets import (
                             QWidget,
                             QVBoxLayout,
                             QApplication,
                             QComboBox,
                             QDoubleSpinBox,
                             QSizePolicy,
                             QHBoxLayout,
                             QSpinBox,
                             QLabel,
                             )
import math
import numpy as np
from matplotlib import pyplot as plt
from scipy import signal as s
import wfdb
import ast
import pandas as pd
import sys


class TunerModule(QWidget):
    def __init__(self, parent=None, signal=[], width=10, height=8, dpi=100, update_info_callback=None, filter_options=None):
        super().__init__(parent)

        self.update_info = update_info_callback
        # Create the figure canvas
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.widgets = {}
    
        # Create the plot structure
        self.axes1 = self.fig.add_subplot(3, 1, 1)
        self.axes2 = self.fig.add_subplot(3, 1, 2)
        self.axes3 = self.fig.add_subplot(3, 1, 3)

        self.mode_options = [
            'Highpass',
            'Lowpass',
            #'Bandpass',
            #'Bandstop'
        ]


        print("Loading filter options")
        self.info = filter_options

        print(self.info)
        
        filterTypeWidget = QWidget()
        filterTypeLayout = QHBoxLayout(filterTypeWidget)
        label = QLabel("Filter Type")
        modeBox = QComboBox()
        modeBox.addItems(self.mode_options)
        modeBox.setCurrentIndex(self.mode_options.index(self.info['mode']))

        modeBox.currentIndexChanged.connect(self.change_mode)

        filterTypeLayout.addWidget(label)
        filterTypeLayout.addWidget(modeBox)
        layout.addWidget(filterTypeWidget)


        self.coeffs = []

        self.signal = signal

        for key in self.info.keys():
            optionWidget = QWidget()
            optionLayout = QHBoxLayout(optionWidget)

            label = False
            if key == 'lower_corner':
                new_widget = QSpinBox()
                new_widget.setMinimum(1)
                new_widget.setMaximum(1000)
            elif key == 'higher_corner':
                new_widget = QSpinBox()
                new_widget.setMinimum(1)
                new_widget.setMaximum(1000)
            elif key == 'attenuation':
                new_widget = QDoubleSpinBox()
                new_widget.setMinimum(.1)
                new_widget.setMaximum(1)
                new_widget.setSingleStep(0.1)
            elif key == 'sampling_freq':
                new_widget = QLabel(str(self.info[key]))
                label = True
            else:
                continue
            
            if label == False:
                new_widget.setValue(self.info[key])
                new_widget.valueChanged.connect(lambda value, opt=key: self.update_settings(opt, value))
            
            label = QLabel(key)

            optionLayout.addWidget(label)
            optionLayout.addWidget(new_widget)
            
            layout.addWidget(optionWidget)
            self.widgets[key] = new_widget
            self.update_plots()
        
    def update_settings(self, key, value):
        """Updates the settings of the model"""
        print(f"Update: {key}, {value}")
        if key not in self.info:
            return

        valid = True
        if key == 'lower_corner':
            # Ensure 'lower_corner' is never greater than 'higher_corner'
            if value >= self.info['higher_corner'] - 3:
                valid = False
                print(f"Cannot set 'lower_corner' higher than 'higher_corner' ({self.info['higher_corner']})")
                self.widgets['higher_corner'].setMinimum(self.info['lower_corner'] + 4)
                self.widgets['higher_corner'].setValue(self.info['lower_corner'] + 4)
            else:
                self.widgets['higher_corner'].setMinimum(self.info['lower_corner'] + 4)
                self.widgets['lower_corner'].setMaximum(self.info['higher_corner'] - 3)

        elif key == 'higher_corner':
            # Ensure 'higher_corner' is never less than 'lower_corner'
            if value <= self.info['lower_corner'] + 3:
                valid = False
                print(f"Cannot set 'higher_corner' lower than 'lower_corner' ({self.info['lower_corner']})")
                self.widgets['lower_corner'].setMaximum(self.info['higher_corner'] - 4)
                self.widgets['lower_corner'].setValue(self.info['higher_corner'] - 4)
            else:
                self.widgets['lower_corner'].setMaximum(self.info['higher_corner'] - 4)
                self.widgets['higher_corner'].setMinimum(self.info['lower_corner'] + 3)
                
        elif key == 'attenuation':
            # Clamp 'attenuation' within the range 0 to 1
            pass
        elif key == 'sampling_freq':
            # Sample frequency should be positive
            if value <= 0:
                print(f"Sample frequency must be positive, given: {value}")
                return
            
        if valid:
            # For any other setting that does not need special handling
            self.info[key] = value
            self.update_plots()

    def change_mode(self, i):
        """Changes the mode of the model"""
        self.info['mode'] = self.mode_options[i]
        self.update_plots()

    def convert_to_digital(self, corner_freq, sampling_freq):
        """Converts analog frequency to digital frequency"""
        #return 2 * math.atan((2 * math.pi * corner_freq)/(2 * sample_freq))
        return 2 * np.pi * corner_freq / sampling_freq

    def attentuation_dB(self, reduction_percentage):
        """Calculates the attentuation in dB"""
        return -20 * math.log10(reduction_percentage)
    
    def compute_order(self, pass_band, stop_band, attentuation):
        """Computes the filter order based on the pass band, stop band, and attentuation specs"""
        if attentuation > -21:   # rectangular
            mainlobe_coef = 4 * math.pi
        elif attentuation > -44: # hanning
            mainlobe_coef = 8 * math.pi
        elif attentuation > -53: # hamming
            mainlobe_coef = 8 * math.pi
        elif attentuation > -74: # blackman
            mainlobe_coef = 12 * math.pi
        else:
            print("Attentuation unachievable with currently available windows")
            exit()

        return math.ceil(mainlobe_coef / (abs(pass_band - stop_band))) - 1
    
    def compute_coeffs(self, freq_digi, order, filter_type):
        """Computes the FIR filter coefficients."""
        coeffs = np.sinc([freq_digi * (n - order/2) / np.pi for n in range(order + 1)]) * (freq_digi / np.pi)
        if filter_type == 'highpass':
            coeffs = -coeffs
            coeffs[int(order/2)] += 1
        return coeffs

    def forward(self):
        """Computes filter coefficients based on the mode and parameters."""
        freq_digi_lower = self.convert_to_digital(self.info['lower_corner'], self.info['sampling_freq'])
        freq_digi_upper = self.convert_to_digital(self.info['higher_corner'], self.info['sampling_freq'])

        attentuation_dB = self.attentuation_dB(self.info['attenuation'])
        order = self.compute_order(freq_digi_lower, freq_digi_upper, attentuation_dB)
        if self.info['mode'] == 'Lowpass':
            coeffs = self.compute_coeffs(freq_digi_lower, order, 'lowpass')
        elif self.info['mode'] == 'Highpass':
            coeffs = self.compute_coeffs(freq_digi_lower, order, 'highpass')
        elif self.info['mode'] == 'Bandpass' or self.info['mode'] == 'Bandstop':
            low_coeffs = self.compute_coeffs(freq_digi_lower, order, 'lowpass')
            high_coeffs = self.compute_coeffs(freq_digi_upper, order, 'highpass')
            if self.info['mode'] == "Bandpass":
                coeffs = low_coeffs - high_coeffs
            elif self.info['mode'] == "Bandstop":
                coeffs = low_coeffs + high_coeffs
        
        self.coeffs = coeffs.tolist()
        self.info['coefs'] = self.coeffs
        
        for key in self.info.keys():
            self.update_info(key, self.info[key])
 

    def update_plots(self):
        """Updates the plots with new information"""
        self.forward()
        convolved = np.convolve(self.signal, self.coeffs)
        sampling_freq = self.info['sampling_freq']

        # Filter Order Plot
        self.axes1.clear()
        self.axes1.set_title(f'Filter Order = {len(self.coeffs)} Latency = {len(self.coeffs)/sampling_freq}s')
        self.axes1.stem([i for i in range(-int(len(self.coeffs)/2), math.ceil(len(self.coeffs)/2) , 1)], self.coeffs)
        self.axes1.set_xlim([-int(len(self.coeffs)/2 + 4), int(len(self.coeffs)/2 + 4)])
        self.axes1.set_ylabel("Coefficients")

        # Signal view plot
        self.axes2.clear()
        self.axes2.plot([i for i in range(len(self.signal))], [self.signal[int(len(self.coeffs)/sampling_freq) + i] for i in range(len(self.signal))], label='Signal', color='lightblue')
        self.axes2.plot([i for i in range(len(convolved))], convolved, label='Convolved', color='orange')
        self.axes2.set_xlim([0, len(self.signal)])
        self.axes2.legend()

        # Frequency response plot
        self.axes3.clear()
        w, h = s.freqz(self.coeffs, worN=1024)
        freqs = w / (2 * np.pi) * sampling_freq
        self.axes3.plot(freqs, np.abs(h))
        self.axes3.axvline(x = self.info['lower_corner'], color='r')
        self.axes3.axvline(x = self.info['higher_corner'], color='g')
        self.axes3.set_xlabel('Frequency (Hz)')
        self.axes3.set_xlim([0, freqs[-1]])
        self.canvas.draw()

def give_one_signal():
    path = '/home/lucas/Desktop/programming/classwork/Senior_project/project/data/'
    sampling_rate=500
    Y = pd.read_csv(path+'ptbxl_database.csv', index_col='ecg_id')
    Y.scp_codes = Y.scp_codes.apply(lambda x: ast.literal_eval(x))

    X = wfdb.rdsamp(path+Y['filename_hr'].iloc[0])

    sig = [X[0][i][0] for i in range(len(X[0]))]
    return sig

class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = TunerModule(signal=give_one_signal())
        self.setup_ui()

    def setup_ui(self):
        # Optionally add navigation toolbar for the matplotlib canvas
        
        self.main_window.show()

if __name__ == "__main__":
    
    app = MainApplication(sys.argv)


    # Update plots with example data
    app.main_window.update_plots()
    
    # Start the main PyQt event loop
    sys.exit(app.exec_())
