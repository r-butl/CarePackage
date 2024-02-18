#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


void convolution(float *input_signal, float *output_signal, float *kernel, int input_length, int kernel_length){
    
    // Implement Error checking

    // Create an new input signal with padding on the front end
    int buffer_length = (input_length + kernel_length - 1) * sizeof(float);        // Calculate buffer size
    float *signal_buffer = (float *)(malloc(buffer_length));                  // allocate buffer
    memset(signal_buffer, 0, buffer_length);                                  // init to 0
    memmove(&signal_buffer[kernel_length - 1], input_signal, input_length * sizeof(float) );    // copy over input signal
    
    float accum;
    float *curr_kernel;       // Stores the address of the current index in the coeff array
    float *curr_index;      // stores the address of the current indec in the input signal array

    for(int i = 0; i < input_length; i++){
        curr_kernel = &kernel[0];                                 // Set the index for coefs to the beginning of the coeffs array
        curr_index = &signal_buffer[i + kernel_length - 1];    // Set index to end of the input overlap window
        accum = 0;

        for(int j = 0; j < kernel_length; j++){
            accum = accum + (*curr_kernel * *curr_index);
            curr_kernel++;                                        // Move forwards through the coeffs array
            curr_index--;                                       // move backwards through the input array
        }
        output_signal[i] = accum;
    }

    free(signal_buffer);     // free up allocated memory

}

float* fivepoint_diff(float *input_signal, float *output_signal, int signal_length, float sampling_period){

    float coef_mult = 1.0 / (8.0 * sampling_period);
    int output_signal_length = signal_length - 4;   // Two pads before the current time step, two pads after

    for( int i = 2; i < signal_length - 2; i++){
        float value = coef_mult * ( - (input_signal[i - 2]) - (2 * input_signal[i -1]) + (2 * input_signal[i + 1]) + (input_signal[i]) );
        
        // printf("%f, %f\n", input_signal[i], value);

        output_signal[i] = value; 
    }
    
}

void squaring(float *input_signal, float *output_signal, int signal_length){
    
    for( int i = 0; i < signal_length; i++){
        float value = input_signal[i] * input_signal[i];
        
        //printf("%f, %f\n", input_signal[i], value);

        output_signal[i] = value; 
    }
}

void moving_window_integration(float *input_signal, float *output_signal, int signal_length, int window_width){
    
    int buffer_length = (signal_length + window_width - 1) * sizeof(float);        // Calculate buffer size
    float *signal_buffer = (float *)(malloc(buffer_length));                  // allocate buffer
    memset(signal_buffer, 0, buffer_length);                                  // init to 0
    memmove(&signal_buffer[window_width - 1], input_signal, signal_length * sizeof(float) );    // copy over input signal
    
    for( int i = 0; i < signal_length; i++){

        float value = 0.0;
        for( int j = 0; j < window_width; j++){
            value += signal_buffer[i + window_width - j];
        }        

        output_signal[i] = value;  
    }

    free(signal_buffer);
}

void detect_QRS(float *input_signal, float *output_indices, int signal_length){

}

void pan_tompkins(float *input_signal, float *output_signal, int signal_length){


};

