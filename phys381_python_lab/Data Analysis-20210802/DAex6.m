% example 1
clear all
close all

fs = 1000.0; % sampling frequency (Hz) 
ts = 1/fs; % set sampling rate and interval
period=10.0; %sampling period
nfft = period/ts; % length of DFT
t=0:ts:period-ts;
h = (1.3)*sin(2*pi*5.0*t) ...       % 5 Hz component
  + (1.7)*sin((2*pi*35.0*t)-0.6) ...   % 35 Hz component
  + (2.5)*randn(size(t));          % Gaussian noise;

figure
plot(t,h)

H = fft(h); % determine the 32-point DFT

% remove the second half because just a copy of the first half
H = H(1:nfft/2);
% Take the magnitude of fft of H
mx = abs(H)*(2.0/nfft);
% Frequency vector
f = (0:nfft/2-1)*fs/nfft;


figure(1);
plot(t,h);
title('Sine Wave Signals');
xlabel('Time (s)');
ylabel('Amplitude');
figure(2);
plot(f,mx);
title('Amplitude Spectrum of Sine Wave signals');
xlabel('Frequency (Hz)');
ylabel('Amplitude');
