#ifndef PAN_TOMPKINS_H
#define PAN_TOMPKINS_H

void convolution(float *input_signal, float *output_signal, float *kernel, int input_length, int kernel_length);

void FPD(float *input_signal, float *output_signal, int signal_length, float sampling_period);

void squaring(float *input_signal, float *output_signal, int signal_length);

void moving_window_integration(float *input_signal, float *output_signal, int signal_length, int window_width);

void detect_peak(float *input_signal, float threshold, int *output_indices, int signal_length, int *num_peaks_found);

#endif