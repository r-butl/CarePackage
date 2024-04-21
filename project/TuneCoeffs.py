from PyQt5.QtWidgets import (
                             QWidget,
                             QVBoxLayout,
                             QPushButton,
                             QSizePolicy,
                             QHBoxLayout,
                             QSpinBox,
                             QCheckBox,
                             QLabel,
                             QDialog,
                             QDialogButtonBox
                             )
import math
import numpy as np

class TunerModel:
    def __init__(self):

        self.mode_options = [
            'Highpass',
            'Lowpass',
            'Bandpass',
            'Bandstop'
        ]
        
        self.mode = 'Lowpass'

        self.lower_corner = 1         # hz
        self.lower_padding = 2        # Padding on either side of the corner frequency for tuning the coeffs

        self.higher_corner = 1        # hz
        self.higher_padding = 2       # padding on either side of the corner frequency for tuning the coeffs

        self.sample_freq = 100
        self.attentuation = 0.7

    def convert_to_digital(self, corner_freq, sample_freq):
        return 2 * math.atan((2 * math.pi * corner_freq)/(2 * sample_freq))

    def attentuation(self, reduction_percentage):
        return 20 * math.log10(1 - reduction_percentage)
    
    def compute_order(self, pass_band, stop_band, attentuation):

        if attentuation > -21:   # rectangular
            mainloab_coef = 4 * math.pi
        elif attentuation > -44: # hanning
            mainloab_coef = 8 * math.pi
        elif attentuation > -53: # hamming
            mainloab_coef = 8 * math.pi
        elif attentuation > -74: # blackman
            mainloab_coef = 12 * math.pi
        else:
            print("Attentuation unachievable with currently available windows")
            exit()

        order = math.ceil(mainloab_coef / (abs(pass_band - stop_band))) - 1

        return order
    
    def compute_coeffs(self, freq_digi, order, high_pass=False):
        
        coeffs = []

        for n in range(order):
            coef = (freq_digi/math.pi) * np.sinc(freq_digi * (n - order/2) / math.pi)

            if high_pass:
                coef = -coef
                if n == order / 2:
                    coef += 1

            coeffs.append(coef)
             
        return coeffs


        
    def forward(self):
        sets_to_compute = []
        if self.mode == 'Lowpass':
            sets_to_compute.append()