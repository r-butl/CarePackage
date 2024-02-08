#from matplotlib import pyplot
import math
import numpy
# https://www.allaboutcircuits.com/technical-articles/design-examples-of-fir-filters-using-window-method/


def convert_to_digital(corner_freq, sample_freq):
    return 2 * math.atan((2 * math.pi * corner_freq)/(2 * sample_freq))

def attentuation(reduction_percentage):
    return 20 * math.log10(1 - reduction_percentage)


sample_freq = 1000      # hz

lower_pass_band = convert_to_digital(1, sample_freq)         # hz
lower_stop_band = convert_to_digital(10, sample_freq)         # hx
lower_corner = (lower_stop_band + lower_pass_band) / 2

upper_pass_band = convert_to_digital(90, sample_freq)         # hz
upper_stop_band = convert_to_digital(110, sample_freq)         # hx
upper_corner = (upper_stop_band + upper_pass_band) / 2

delta_2 = attentuation(.999)    # Stop band reduction

# Determins order based on window type
mainloab_coef = float()

if delta_2 > -21:   # rectangular
    mainloab_coef = 4 * math.pi
elif delta_2 > -44: # hanning
    mainloab_ceof = 8 * math.pi
elif delta_2 > -53: # hamming
    mainloab_coef = 8 * math.pi
elif delta_2 > -74: # blackman
    mainloab_coef = 12 * math.pi
else:
    print("Attentuation unachievable with currently available windows")
    exit()

# Compute Order
upper_order = math.ceil(mainloab_coef / (abs(upper_pass_band - upper_stop_band))) - 1
lower_order = math.ceil(mainloab_coef / (abs(lower_pass_band - lower_stop_band))) - 1

order = max(upper_corner, lower_order)

def compute_coef(w_u, w_l, order, n):
    return (w_u/math.pi) * numpy.sinc(w_u * (n - order/2) / math.pi) - (w_l/math.pi) * numpy.sinc(w_l * (n - order/2) / math.pi)

coefs = [compute_coef(upper_corner, lower_corner, order, i) for i in range(order)]

print(coefs)
from matplotlib import pyplot as plt

plt.stem(coefs)
plt.show()