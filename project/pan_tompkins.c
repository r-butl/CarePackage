#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


#define FIR_COEFS_LENGTH 100                                // tuned filter is 100 coefs long

#define INPUT_SIGNAL_LENGTH 1000                                  // 100 samples/sec * 10 secs

#define INPUT_SIGNAL_BUFFER_LENGTH (INPUT_SIGNAL_LENGTH - 1 + FIR_COEFS_LENGTH)

// float input_sample_buf[INPUT_SIGNAL_BUFFER_LENGTH];  // Padded buffer for convolution
// Returns the length of an array
//	- When instantiating an array in the Python script, it is not necessary to append the NULL character
// void init_buff(void){
//     memset(input_sample_buf, 0, sizeof(input_sample_buf));
// }

void bandpass_fir_filter(float *input_signal, float *output_signal, float *coeffs, int input_length, int coef_length){
    
    //init_buff();            // Set buffer to all 0s
    int sample_buffer_length = (input_length + coef_length - 1) * sizeof(float);
    float *input_sample_buf = (float *)(malloc(sample_buffer_length));
    memset(input_sample_buf, 0, sample_buffer_length);
    memmove(&input_sample_buf[coef_length - 1], input_signal, input_length * sizeof(float) );    // Add padding to the input signal
    
    float accum;
    float *curr_coef;       // Stores the address of the current index in the coeff array
    float *curr_index;      // stores the address of the current indec in the input signal array


    for(int i = 0; i < input_length; i++){
        curr_coef = &coeffs[0];                                 // Set the index for coefs to the beginning of the coeffs array
        curr_index = &input_sample_buf[i + coef_length - 1];    // Set index to end of the input overlap window
        accum = 0;

        for(int j = 0; j < coef_length; j++){
            accum = accum + (*curr_coef * *curr_index);
            curr_coef++;
            curr_index--;
        }
        output_signal[i] = accum;
    }


    /*
    for(int i = 0; i < input_length; i++){
        output_signal[i] = input_sample_buf[i + coef_length - 1];
    }
       
    for(int i = 0; i < input_length; i++){
        printf("%f, %f\n", input_sample_buf[i + coef_length - 1], input_signal[i])    ;
    }
 
    for(int i = 0; i < input_length; i++){
        printf("%f, %f\n", input_sample_buf[i], input_signal[i])    ;
    }
    */
    //memcpy(padded_input, 0, signal_length * sizeof(float));

    free(input_sample_buf);

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

