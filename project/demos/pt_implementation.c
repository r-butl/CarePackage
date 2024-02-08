#include <stdio.h>

// Returns the length of an array
//	- When instantiating an array in the Python script, it is not necessary to append the NULL character


void pan_tompkins(float *input_signal, int length, float *output_signal);

void FIR_filter(float *coefs, int len_coefs, float *input_signal, float *output_signal);

