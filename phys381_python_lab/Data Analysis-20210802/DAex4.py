# -*- coding: utf-8 -*-
"""
%   Demonstration script to create some simulated data
%   and then fit a polynomial to it.


Created on Sun Jul 12 11:13:47 2020

@author: ajm226
"""



import numpy as np

import matplotlib.pyplot as plt

#
#   generate the data
#
n = 100                   # number of data points
x = np.random.ranf(n)*15-5;        # random x data values in range -5 to 10 uniformly distibuted
xx = np.arange(-5.5,10.501,0.01)       # x vector to use for plotting
p = [1, -10, -10, 20]        # polynomial coefficients





y = np.polyval(p,x)          # y data values
sigma = np.random.rand(n)*25;      # random uniformly distributed uncertainties in range 0 to 25
error=np.random.normal(0.0,1.0,n)*sigma   # add gaussian-distributed random noise
y=y+error

#    plot the data points and the cubic polynomial

plt.figure()
plt.errorbar(x,y,xerrr=None,yerr=sigma,linestyle='none', marker='*')
plt.plot(xx,np.polyval(p,xx),'m-')
plt.savefig('DAex4.png',dpi=600)
#    fit a 4-coefficient polynomial (i.e. a cubic) to the data
#    and quantify the quality of the fit
