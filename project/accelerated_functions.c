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

int* wavelet(int* input)
{

	return NULL;

}

int* median(int* input)
{
        int window = 3;
        int* output[get_length(input) - window + 1];

        for(int i = 1; i < get_length(input) - window; i++){
                
                output[i - 1] = 
        }
	return NULL;
}
