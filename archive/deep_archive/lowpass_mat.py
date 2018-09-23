# filename: lowpass_mat
# By: Abhay Gupta
# Date: 07/19/2018
#
#
# Description: matlab to python filter change
# Specifcially: Kaiser order, FIR filter
#

import matplotlib.pyplot as plt
from scipy import signal
import numpy as np


def lowpass(f_cuts, f_samp, devs):
    from scipy import signal
    import math as m

    Ny = f_samp / 2

    # Python only takes a single parameter to control pb & sb ripple; therefore take minimum
    ripple_min = min(devs)
    ripple_min = -20 * m.log10(ripple_min)

    # Transition width between pb & sb
    trans_width = f_cuts[1] - f_cuts[0]
    trans_width = trans_width  # /Ny

    # Determine length of filter & parameter for Kaiser window
    numtaps, beta = signal.kaiserord(ripple_min, trans_width)
    print('rip', ripple_min)
    print('trans', trans_width)
    print(numtaps)
    print(beta)

    cut = (f_cuts[1] + f_cuts[0]) / 2
    cut = cut * Ny
    cutoff = cut

    # Create FIR filter
    taps = signal.firwin(numtaps, cutoff=cut, window=('kaiser', beta),
                         scale=False, nyq=Ny)

    print('taps', len(taps))
    return (taps, cutoff, trans_width, ripple_min)


# matlab inputs:
f_samp = 100  # Sampling rate
mags = [1, 0]  # Define gain after cutoff
devs = [0.001, 0.1]  # Define ripple tol (Pb, Sb)
f_cuts = [0.1, 0.7]

# lowpass filter function
taps, cutoff, width, ripple_min = lowpass(f_cuts, f_samp, devs)

plt.plot(taps)
plt.show()
quit()

w, h = signal.freqz(taps, worN=16000)
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
