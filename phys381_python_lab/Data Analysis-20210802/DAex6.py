# -*- coding: utf-8 -*-
"""
Example Fourier Transform code for PHYS381 Data analysis assessment


Created on Sun Jul 12 11:52:42 2020

@author: ajm226
"""
import numpy as np
import matplotlib.pyplot as plt


fs = 1000.0 # sampling frequency (Hz) 
ts = 1/fs # set sampling rate and interval
period=10.0 #sampling period
nfft = period/ts # length of DFT
t=np.arange(0,period,ts)
h = ((1.3)*np.sin(2*np.pi*5.0*t) + (1.7)*np.sin((2*np.pi*35.0*t)-0.6) + (2.5)*np.random.normal(0.0,1.0,t.shape))          
# combination of a 5 Hz signal a 35Hz signal and Gaussian noise



plt.figure(1)
plt.plot(t,h)
plt.savefig('DAex6.png',dpi=600)


H = np.fft.fft(h) # determine the Discrte Fourier Transform


# Take the magnitude of fft of H
mx = abs(H[0:np.int(nfft/2)])*(2.0/nfft)  # note only need to examien first half of spectrum
# Frequency vector
f = np.arange(0,np.int(nfft/2))*fs/nfft


plt.figure(2)
plt.plot(t,h);
plt.title('Sine Wave Signals');
plt.xlabel('Time (s)');
plt.ylabel('Amplitude');
plt.figure(3)
plt.plot(f,mx)
plt.title('Amplitude Spectrum of Sine Wave signals');
plt.xlabel('Frequency (Hz)');
plt.ylabel('Amplitude');
plt.savefig('DAex6_fft.png',dpi=600)