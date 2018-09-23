# filename: filt
# by: Abhay Gupta
#
# Description: All custom filter functions


# Use the FIR filter on the data, where you take both the first have and 
# ... second half of data
def data_fil(data, h, pass_zero=False):
    from scipy import signal
    import statistics as stats
    from utils.math_functions.general_math import my_round

    # Filter the ecg signal
    filtered_data = signal.lfilter(h, 1, data)
    filtered_data = filtered_data.tolist()

    # Invert the ecg signals, to filter the signal backwards
    data_inverted = list(reversed(data))
    filtered_inverted_data = signal.lfilter(h, 1, data_inverted).tolist()

    # Reinvert the inverted filtered ecg signal, to right placement
    reinverted_filtered_data = list(reversed(filtered_inverted_data))

    # Find the offset value of the filter
    filter_delay = my_round(len(h) / 2)

    if (filter_delay > my_round(len(data) / 2)):
        filter_delay = my_round(len(data) / 2)

    adjusted_filtered_data = filtered_data[filter_delay - 1:]
    # low pass filter settings....
    # Read just the positioning due to phase offset
    if (pass_zero == True):
        adjusted_reinverted_filtered_data = \
            [stats.mean(reinverted_filtered_data[0:-(filter_delay + 20)])] \
            * (filter_delay) + reinverted_filtered_data[0:-filter_delay]

        cleaned_filtered_data = \
            adjusted_filtered_data[
            0:my_round(len(adjusted_filtered_data) / 2)] + \
            adjusted_reinverted_filtered_data[
            my_round(len(adjusted_filtered_data) / 2):]
    else:
        adjusted_reinverted_filtered_data = \
            [stats.mean(reinverted_filtered_data[0:-(filter_delay + 20)])] \
            * (filter_delay - 1) + reinverted_filtered_data[0:-filter_delay + 1]

        cleaned_filtered_data = \
            adjusted_filtered_data[
            0:my_round(len(adjusted_filtered_data) / 2)] + \
            adjusted_reinverted_filtered_data[
            my_round(len(adjusted_filtered_data) / 2):]

    return (cleaned_filtered_data, filtered_data, reinverted_filtered_data, h)


# Low pass - Kaiser window, FIR filter
def lowpass(data, f_cuts, fsamp, ripple_tol):
    from scipy import signal
    import math as m

    # Nyquist frequency
    Ny = fsamp / 2

    # Width of the transition band
    width = f_cuts[1] - f_cuts[0]

    # Single parameter to controlling max allowable pb & sb ripple
    ripple_tol = min(ripple_tol)
    ripple_tol = -20 * m.log10(ripple_tol)

    # Determine the length of filter & shape parameter for kaiser window
    numtaps, beta = signal.kaiserord(ripple_tol, width)

    # Center of transition window
    cutoff = (f_cuts[1] + f_cuts[0]) / 2

    # Create FIR Filter
    h = signal.firwin(numtaps, cutoff, window=('kaiser', beta), scale=False, \
                      pass_zero=True)

    return data_fil(data, h, pass_zero=True)


# High pass FIR filter
def highpass(data, fs, cutoff):
    from scipy import signal

    order = 900
    numtaps = order + 1
    Ny = fs / 2
    cutoff = cutoff / (Ny)
    coeff = signal.firwin(numtaps, cutoff, pass_zero=False)

    return data_fil(data, coeff)


# From Python docs, analyze the filter deviation from set ripple tolerances
def filter_analysis(data, taps, f_samp, f_cuts, ripple_tol, N):
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal

    ripple_min = min(ripple_tol)
    width = (f_cuts[1] - f_cuts[0]) * (f_samp / 2)
    cutoff = (f_cuts[1] + f_cuts[0]) / 2
    cutoff = cutoff * f_samp / 2

    w, h = signal.freqz(taps, worN=N)
    w *= 0.5 * f_samp / np.pi

    ideal = w < cutoff  # The "ideal" frequency response.
    deviation = np.abs(np.abs(h) - ideal)
    deviation[(w > cutoff - 0.5 * width) & (w < cutoff + 0.5 * width)] = np.nan

    plt.plot(w, 20 * np.log10(np.abs(deviation)))
    plt.xlim(0, 0.5 * f_samp)
    # plt.ylim(-1*ripple_min - 30, -1*ripple_min + 10)
    plt.grid(alpha=0.25)
    plt.axhline(-ripple_min, color='r', ls='--', alpha=0.3)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Deviation from ideal (dB)')
    plt.title('Lowpass Filter Frequency Response')
    plt.show()
