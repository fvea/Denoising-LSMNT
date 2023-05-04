import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.fft import fft

import warnings
warnings.filterwarnings("ignore")

from PyEMD import EMD
from scipy.stats import kurtosis


def compute_fft(signal, sr):
    N = len(signal)
    t = np.arange(0,N)/sr  # time x-axis
    X = np.abs(fft(signal))/N; X = X[0:math.ceil(N/2)] # magnitude y-axis
    f = np.arange(0,N)/N*sr; f = f[0:math.ceil(N/2)]   # frequency x-axis
    return t, f, X


def plot_signal_waveform_fft(signal, sr, sample_name, fft_xlim=(0, 1000)):

    # get fft variables
    t, f, X = compute_fft(signal, sr)
    # X = amplitude_to_db(X)

    # plot time waveform and frequency spectrum of signal
    plt.figure(1)
    plt.subplot(211)
    plt.plot(t, signal); plt.ylim(-1.5,1.5); #plt.xlim([0, 1])
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')
    plt.title(f'Signal Time Waveform ({sample_name})')

    plt.subplot(212)
    plt.plot(f, X);  plt.xlim(fft_xlim)
    plt.title(f'Frequency Spectrum ({sample_name})')
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.show()

def envelope_analysis(signal):
    N = len(signal)
    xn = np.abs(hilbert(signal))
    # envelope signal FFT
    X = np.abs(fft(xn-np.mean(xn)))/N; 
    X = X[0:math.ceil(N/2)]
    return xn, X

def plot_envelope_signal(signal, sr, imf_idx, rpm=None, num_balls=None, fft_xlim=(0, 500)):

    # compute envelope signal and envelope signal frequency spectrum 
    env, env_fft = envelope_analysis(signal)

    # get raw signal fft variables
    t, f, _ = compute_fft(signal, sr)

    plt.figure(2)
    plt.subplot(211)
    plt.plot(t, signal, c='gray'); plt.ylim(-1.5,1.5)
    plt.plot(t, env, 'r'); plt.xlim([0, 1])
    plt.ylabel('Amplitude')
    plt.xlabel('Time (s)')
    signal_name = 'Raw Signal' if imf_idx == -1 else f'IMF{imf_idx}'
    plt.title(f'Envelope Signal {signal_name}')

    plt.subplot(212)
    plt.plot(f, env_fft);  plt.xlim(fft_xlim); plt.ylim([0, 0.020])
    
    if rpm and num_balls:
        ir_fault_freq = (.6 * num_balls * rpm) / 60
        or_fault_freq = (.4 * num_balls * rpm) / 60
        bp_fault_freq = (2.6 * rpm) / 60
        cg_fault_freq = (.41 * rpm) / 60
        plt.axvline(ir_fault_freq, c='black', ls='--', linewidth=2, label="Inner Race")
        plt.axvline(or_fault_freq, c='red', ls='--', linewidth=2, label="Outer Race")
        plt.axvline(bp_fault_freq, c='yellow', ls='--', linewidth=2, label="Ball Pass")
        plt.axvline(cg_fault_freq, c='orange', ls='--', linewidth=2, label="Cage")
        plt.legend()
        
    plt.title(f'Frequency Spectrum')
    plt.ylabel('Amplitude')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.show(block=False)


def emd_denoise(signal):
    N = len(signal)
    emd = EMD(MAX_ITERATION=100, energy_ratio=20)                    # EMD
    imf = emd.emd(signal, max_imf=5)                    
    XX = np.zeros([len(imf), math.ceil(N/2)])                        # imfs FFT storage
    k = np.zeros(len(imf))                                           # imfs Kurtosis storage
    for ix in range(len(imf)):
        tmp = abs(fft(imf[ix]))/N; tmp = tmp[0:math.ceil(N/2)]
        k[ix] = kurtosis(imf[ix], fisher=False)
        XX[ix] = tmp

    ind = np.where(k == np.max(k))[0][0] # index of imf with highest kurtosis
    return imf, k, imf[ind]


def plot_emd_result(signal, sr, imf):

    N = len(signal)
    t = np.arange(0, N)/sr   # time x-axis

    plt.figure(1, figsize=[6, 8])
    plt.subplot(611); plt.plot(t, signal); plt.ylabel('Raw'); plt.xlim(0, 1)
    # plt.title(f"Kurtosis: {kurtosis(signal, fisher=False): .2f}")

    subplot_num = 612
    for ix in range(0, 5):
        plt.subplot(subplot_num); plt.plot(t, imf[ix]); plt.ylabel(f'IMF{ix}'); plt.xlim(0, 1)
        # plt.title(f"Kurtosis: {k[ix]: .2f}")
        subplot_num += 1

    plt.xlabel('Time (s)')
    plt.suptitle(f'Signal Decomposition Results', x=0.57)
    plt.tight_layout()
    plt.show(block=False)