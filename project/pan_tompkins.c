#include <stdio.h>
#include <stdlib.h>

#define FIR_COEFS_LENGTH 100
// Returns the length of an array
//	- When instantiating an array in the Python script, it is not necessary to append the NULL character

void bandpass_fir_filter(float *input_signal, float *output_signal, int signal_length);

void differentiate(float *input_signal, float *output_signal, int signal_length);

void squaring(float *input_signal, float *output_signal, int signal_length);

void moving_window_int(float *input_signal, float *output_signal);

void detect_QRS(float *input_signal, float *output_indices, int signal_length);

void pan_tompkins(float *input_signal, float *output_signal, int signal_length){

    float *post_bandpass = (float *)(mallac(signal_length - FIR_COEFS_LENGTH) * sizeof(float));




};

