#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "ProcessBlockImplementations.h"
#include <stdbool.h>

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

void FPD(float *input_signal, float *output_signal, int signal_length, float sampling_period){

    float coef_mult = 1.0 / (8.0 * sampling_period);
    int output_signal_length = signal_length - 4;   // Two pads before the current time step, two pads after

    for( int i = 2; i < signal_length - 2; i++){
        float value = coef_mult * (input_signal[i - 2] - 8 * input_signal[i - 1] + 8 * input_signal[i + 1] + input_signal[i + 2] );
        
        output_signal[i] = value; 
    }
    
}

void squaring(float *input_signal, float *output_signal, int signal_length){
    
    for( int i = 0; i < signal_length; i++){
        float value = input_signal[i] * input_signal[i];
        
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

void central_diff(float *input_signal, float *output_signal, int signal_length, float sampling_period){
    if(signal_length < 3){
        printf("Error: Signal length must be at least 3.\n");
        return;
    }

    float sample_rate = 1.0 / sampling_period;

    output_signal[0] = 0;
    output_signal[signal_length - 1] = 0;

    for(int i = 1; i < signal_length - 1; i++){

        output_signal[i] = (input_signal[i+1] - input_signal[i-1]) * (sample_rate / 2.0);
    }
}

float findMaxValue(float arr[], int n) {
    float max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    return max;
}

// void detect_peak(float *input_signal, float threshold, int *output_indices, int signal_length, int *num_peaks_found){
//     // Pass in a signal and the output is a list of indices that are the peaks of the waves in the signal

//     int current_indice = 0;
//     float max_value = findMaxValue(input_signal, signal_length) * threshold;

//     for(int i = 4; i < signal_length - 4; i++){
//         float left = input_signal[i-1];
//         float current = input_signal[i];
//         float right = input_signal[i+1];

//         if( left < current && 
//             right < current &&
//             current > max_value){

//             output_indices[current_indice++] = i;

//             if(current_indice == 100) break;

//         }
//     }

//     *num_peaks_found = current_indice;
// }


void detect_peak(float *input_signal, int window_size, int *output_indices, int signal_length, int *num_peaks_found){
    // Pass in a signal and the output is a list of indices that are the peaks of the waves in the signal

    int current_index = 0;
    int half_window = window_size / 2;

    for(int i = half_window; i < signal_length - half_window; i++){
        float current = input_signal[i];
        bool is_peak = true;

        // Check against the window around the current point
        for (int j = -half_window; j <= half_window; j++) {
            if (j != 0 && input_signal[i + j] >= current) {
                is_peak = false;
                break;
            }
        }

        if (is_peak) {
            output_indices[current_index++] = i;

            // Stop adding peaks if we reach the maximum storage capacity
            if (current_index == 100) break;
        }
    }

    *num_peaks_found = current_index;
}
