from dispatcher import data_dispatcher
import time
from matplotlib import pyplot as plt
import random

def view_signal(signal):
    # Signal, Timestep, value for each of the 12 leads
    sig = [signal[0][i][0] for i in range(len(X[0]))]
    print(len(sig))

    from scipy.fft import fft, ifft
    fft_sig = fft(sig)

    import matplotlib.pyplot as plt
    plt.plot(sig)
    plt.xlabel("Time (milliseconds)")
    plt.ylabel("Voltage (millivolts)")
    plt.show()

def generate_unique_colors(n):
    """Generate n unique random colors."""
    colors = set()
    while len(colors) < n:
        colors.add((random.random(), random.random(), random.random()))
    return list(colors)

if __name__ == "__main__":

    path = '/home/lucas/Desktop/programming/classwork/Senior_project/project/data/'
    data_dispatch = data_dispatcher(    path=path,
                                        sampling_rate=100)

    run_test = True

    if run_test == True:

        # Generate Test Information
        batch_sizes = [(i * 200)for i in range(1,8)]
        print(batch_sizes)
        test_count = 10
        times = [0] * test_count
        colors = generate_unique_colors(len(batch_sizes))

        for n in range(len(batch_sizes)):

            # Update Batchsize
            data_dispatch.reset()

            print("\n==============================")
            print(f"New Batchsize {batch_sizes[n]}")

            for i in range(test_count):
                # Run one test

                def time_dispatch(num_elements, dispatcher):
                    
                    start_time = time.time()
                    previous_time = start_time
                    dispatcher.reset()

                    for _ in range(num_elements):
                        
                        dispatcher.test_run()
                        #print(f"{f} time: {round(time.time() - previous_time, 7)}")
                        previous_time = time.time()
                        
                        #print()
                
                    elasped_time = time.time() - start_time
                
                    print(f"---- {num_elements} signals in {round(elasped_time, 2)} seconds ----")
                
                    return elasped_time
                
                times[i] = time_dispatch(   num_elements=100, 
                                            dispatcher=data_dispatch)
                
            print(times)

            plt.scatter(x=[i for i in range(test_count)], 
                        y=times, 
                        label=batch_sizes[n],
                        color=colors[n])
            
        print("Finished")
        
        #   Plot
        plt.ylim([0,1])
        plt.title(f"Speed per Batch Size")
        plt.xlabel("Trials")
        plt.ylabel("Time (seconds)")
        plt.legend()
        plt.show()
    else:
        data_dispatch.test_run()
