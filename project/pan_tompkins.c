#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


#define FIR_COEFS_LENGTH 100                                // tuned filter is 100 coefs long

#define INPUT_SIGNAL_LENGTH 1000                                  // 100 samples/sec * 10 secs

#define INPUT_SIGNAL_BUFFER_LENGTH (INPUT_SIGNAL_LENGTH - 1 + FIR_COEFS_LENGTH)

float input_sample_buf[INPUT_SIGNAL_BUFFER_LENGTH];  // Padded buffer for convolution
// Returns the length of an array
//	- When instantiating an array in the Python script, it is not necessary to append the NULL character
void init_buff(void){
    memset(input_sample_buf, 0, sizeof(input_sample_buf));
}

void bandpass_fir_filter(float *input_signal, float *output_signal, float *coeffs, int input_length, int coef_length){
    
    init_buff();            // Set buffer to all 0s

    memcpy(&input_sample_buf[coef_length - 1], input_signal, input_length * sizeof(float) );    // Add padding to the input signal
    
    for(int i = 0; i < input_length; i++){
        output_signal[i] = input_sample_buf[i + coef_length - 1];
    }
    
    /*
    for(int i = 0; i < INPUT_SIGNAL_BUFFER_LENGTH; i++){
        printf("%f\n", input_sample_buf[i]);
    }
    */

    //memcpy(padded_input, 0, signal_length * sizeof(float));


    return output_signal;

}

void differentiate(float *input_signal, float *output_signal, int signal_length){

}

void squaring(float *input_signal, float *output_signal, int signal_length){

}

void moving_window_int(float *input_signal, float *output_signal){

}

void detect_QRS(float *input_signal, float *output_indices, int signal_length){

}

void pan_tompkins(float *input_signal, float *output_signal, int signal_length){


};

