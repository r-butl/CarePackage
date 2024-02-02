from dispatcher import data_dispatcher

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

def time_dispatch(num_elements, dispatcher):
    import time
    start_time = time.time()
    for _ in range(num_elements):
        dispatcher.queue_signals_to_process()
        dispatcher.prep_to_send()

    elasped_time = time.time() - start_time
    print(f"---- {num_elements} signals in {elasped_time} seconds ----")
    dispatcher.reset()
    return elasped_time

if __name__ == "__main__":

    path = '/home/lucas/Desktop/Senior_project/data/'
    data_dispatch = data_dispatcher(path,
                                    batch_size=100,
                                    sampling_rate=100)

    run_test = False
    if run_test == True:
        times = list()
        batch_sizes = [100,300, 500, 700, 1000]
        test_count = 10

        for _ in range(test_count):
            times.append(time_dispatch(10000, data_dispatch))

        from matplotlib import pyplot as plt
        plt.scatter([i for i in range(test_count)], times)
        plt.title("Batch Size: 1000")
        plt.xlabel("Trials")
        plt.ylabel("Time (seconds)")
        plt.show()

    data_dispatch.run()