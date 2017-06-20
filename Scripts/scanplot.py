import pylab as plt
import numpy as np

itrt=101
nm=input("File name: ")
num_lines = sum(1 for line in open(nm))
li=np.sqrt(num_lines/2)
print(li)
x,y,z= np.loadtxt(nm, delimiter='\t').T
yb,xb,zb=[],[],[]
yf,xf,zf=[],[],[]
for i in range(itrt):
    for j in range(itrt):
        k = (2 * i + 1) * 101 + j
        zb.insert(0, z[k])
        xb.insert(0, x[k])
        yb.insert(0, y[k])
    for j in range(itrt):
        k=2*i*101+j
        zf.append(z[k])
        xf.append(x[k])
        yf.append(y[k])
za=[(zf[i]+zb[i])/2 for i in range(itrt*itrt)]
zt=np.asarray(zf)
zu=np.asarray(zb)
zo=np.asarray(za)
nrows=itrt
ncols=itrt
grid = zt.reshape((nrows, ncols))
plt.imshow(grid, extent=(min(xf), max(xf), max(yf), min(yf)))
plt.colorbar()
plt.show()
grid = zu.reshape((nrows, ncols))
plt.imshow(grid, extent=(min(xb), max(xb), max(yb), min(yb)))
plt.colorbar()
plt.show()
grid = zo.reshape((nrows, ncols))
plt.imshow(grid, extent=(min(xb), max(xb), max(yb), min(yb)))
plt.colorbar()
plt.show()