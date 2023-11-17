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

	return NULL;
}