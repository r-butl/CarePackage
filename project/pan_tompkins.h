#ifndef PAN_TOMPKINS_H
#define PAN_TOMPKINS_H

struct signal_state {
    int peak_i;                 // Integrator peak
    int peak_f;                 // Filtered signal peak
    int threshold_i1;           // Integrator full threshold value
    int threshold_i2;           // Integrator half threshold value
    int threshold_f1;           // Filtered full threshold value
    int threshold_f2;           // Filtered half threshold value
    int spk_i;                  // Integrator signal peak estimate
    int spk_f;                  // Filfered signal peak estimate
    int npk_i;                  // Integrator noise peak estimate
    int npk_f;                  // Filtered noise peal estimate 
};

void pan_tompkins(float *input_signal, int *output_indices, int signal_length);

void convolution(float *input_signal, float *output_signal, float *kernel, int input_length, int kernel_length);

float* fivepoint_diff(float *input_signal, float *output_signal, int signal_length, float sampling_period);

void squaring(float *input_signal, float *output_signal, int signal_length);

void moving_window_integration(float *input_signal, float *output_signal, int signal_length, int window_width);

void detect_QRS(float *input_signal, int *output_indices, int signal_length, int *num_peaks_found);

#endif