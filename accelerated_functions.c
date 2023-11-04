#include <stdio.h>

// Returns the length of an array
//	- When instantiating an array in the Python script, it is not necessary to append the NULL character
int get_length(int *a){

        int length = 0;
        while(a[length] != '\0'){
                length += 1;
        }

        return length;
}

int* low_pass(int* input, int sample_per_sec, int w0)
{
/*
	INPUT:
		input 		- integer array	
		sample_per_sec - Sample frequency of the signal
		w0 			- Desired corner frequency of the signal

	y(nT) = 2y(nT- T) - y(nT - 2T) + x(nT) - 2x(nT - 6T) + x(nT - 12T)

	T - sampling period 

	
*/

	return NULL;
}

int* high_pass()
{

	return NULL;
}

int* deriv_filter()
{

	return NULL;
}

int* square()
{

	return NULL;
}

