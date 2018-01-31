import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt

#Fitting function
def lorentz(p,x):
    return p[1]*(5.35*10**-15/2/(np.pi**2))/ (p[0]**2 + (x)**2) #5.35*10**-15 is a calculated diffusion constant

def errorfunc(p,x,z):
        return lorentz(p,x)+z

axis=["x", "y", "z"]
for i in range(15,16): #looping over data files I have
    x=np.loadtxt("PowerSpectra_Data_"+str(i)+".dat", delimiter=',') #The simple way for me to load data into an array
    for indx, ax in enumerate(axis): #use of array axis to have both name of an axis and its index in the data array
        indx = 2 #This line prevents looping over all axes and works only with one in this case Z
        y=1000*x[indx,::] # "x" - is the data I load it has a weird structure so,
        #I manually extract the needed line corresponding to X,Y or Z (should have reshaped but never did)
        print(y.size) #Sometimes I measure for a different time -
        #Most of the time its 100 000 points but sometimes twice as much (2 sec) - just to keep track
        ffty=np.fft.fft(y) #FFT
        powy=abs(ffty)**2/ffty.size/ffty.size #Power spectrum - not sure if I renormalize correctly
        #Never really looked into it since for now I settle for "A.U."
        window=100
        meanymean = np.convolve(abs(ffty), np.ones((window,)) / window, mode='valid') #My attempt at weighted running mean through convolution 
        ffty[10000:]=0 #Just cleaning up the spectrum to see the better the oscillation in a time plot
        plt.loglog(np.arange(1, 50000).T, powy[1:50000]) #weird shape of x means I need to transpose arange
        plt.show()
        #FITTING PART
        xfit=np.arange(0,50000)
        p0=[80,10**15]  #initial guess - first is frequency, second scalling constant
        #Fitting that I use - it does not really work
        solp, ier = scipy.optimize.leastsq(errorfunc,p0,args=(xfit.T,powy[0:50000]),Dfun=None,full_output=False,ftol=1e-9,xtol=1e-9,maxfev=100000,epsfcn=1e-10,factor=0.1)
        plt.loglog(np.arange(1, 50000).T, powy[1:50000])
        print(solp)
        plt.loglog(xfit, lorentz(solp,xfit), 'g--', linewidth=2)
        plt.show()