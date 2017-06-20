from PyDAQmx import *
import numpy as np
from msvcrt import getch
import pylab as plt
"""
Getch for control of piezo from keyboard
So as far as I understand in Unicode
it goes like 224 (special key code) + some break + actual code
This parses stuff that comes after 224
Special key parses by two getch(), normal by one (dont know why):
UP - 72, Down - 80, Left - 75, Right - 77, PageUp - 73, PageDown - 81
Enter not special is 13 in decimal from the start
Esc not special - 27
Plus - 43, Minus - 45
"""

V0=5.0
V1=5.0
o0=Task()
o1=Task()
o0.CreateAOVoltageChan("/Dev1/ao0", "V0", 0.0, 10.0, DAQmx_Val_Volts, None)
o1.CreateAOVoltageChan("/Dev1/ao1", "V1", 0.0, 10.0, DAQmx_Val_Volts, None)
o0.WriteAnalogScalarF64(1,0,V0,None)
o1.WriteAnalogScalarF64(1,0,V1,None)
input("Manualy find rough focus and press Enter")
print("Fine focus is done by piezo. Arrows control. +,- change step Esc,Enter - exit")
key=ord(getch())
step=0.2
while key!=13 and key!=27:
    if key==224:
        key=ord(getch())
        if key==72:
            print("Up")
            V0+=step
        elif key==80:
            print("Down")
            V0-=step
        elif key==77:
            print("Right")
            V1+=step
        elif key==75:
            print("Left")
            V1-=step
        elif key==73:
            print("No In yet")
        elif key==81:
            print("No Out yet")
        else:
            print("Jee... that is some wierd key you've pressed... try again")
    elif key==43 or key==45:
        while key==43 or key==45:
            if key==43:
                step+=0.01
            else:
                step-=0.01
            print("Step changed to: " + str(round(step, 4)) + " V")
            key = ord(getch())
    else:
        print("Unrecognized input")
    if V0 > 0 and V0 < 10 and V1 > 0 and V1 < 10:
        o0.WriteAnalogScalarF64(1, 0, V1, None)
        o1.WriteAnalogScalarF64(1, 0, V0, None)
    else:
        print("You tried leave allowed range")
    print("X Voltage: "+str(round(V0, 4))+"Y Voltage: "+str(round(V1, 4)))
    key = ord(getch())
num=input("Name of file to write to: ")
nm=num +".txt"
dat = open(nm, 'w')
itrt=int(input("Number of iterations: "))
vol=float(input("What volt range do you want to scan? (<10): "))
#Create array of values for output e.g. way of reference and voltages to apply
Vo0=[V0-vol/2+vol*x/(itrt-1) for x in range(itrt)] #Array of voltages depending on iterations in limit [-10,10]
Vo1=[V1-vol/2+vol*x/(itrt-1) for x in range(itrt)] #V0 - x for piezo, V1 - y
Vo1r=Vo1[::-1]
while min(Vo1)<0 or min(Vo0) <0 or max(Vo1)>10 or max(Vo0)>10:
    print(Vo0, Vo1)
    print("Chosen range cannot be used. Choose smaller range.")
    vol = float(input("What volt range do you want to scan? (<10): "))
    Vo0 = [V0 - vol / 2 + vol * x / (itrt - 1) for x in range(itrt)]  # Array of voltages depending on iterations in limit [-10,10]
    Vo1 = [V1 - vol / 2 + vol * x / (itrt - 1) for x in range(itrt)]
print(Vo0, Vo1)
read = int32()
i2=Task()
i2.CreateAIVoltageChan("Dev1/ai2", "", DAQmx_Val_RSE, -5.0, 5.0, DAQmx_Val_Volts, None)
i2.CfgSampClkTiming("", 100000, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 1000000)
data=np.zeros(1000)
input("Start?")
#input("Find center of the focus and press Enter:")
i0=0
j0=0
forward=[]
reverse=[]
for i in Vo0:
    o1.WriteAnalogScalarF64(1, 0, i, None)
    for j in Vo1:
        o0.WriteAnalogScalarF64(1,0,j,None)
        i2.ReadAnalogF64(1000, -1, DAQmx_Val_GroupByChannel, data, 1000, byref(read), None)
        dat.write(str(i) + "\t" + str(j) + "\t" + str(np.average(data)) + "\n")
        print("Point: "+str(i0)+":"+str(j0))
        forward.append(j0)
        j0+=1
    for k in Vo1r:
        o0.WriteAnalogScalarF64(1,0,k,None)
        i2.ReadAnalogF64(1000, -1, DAQmx_Val_GroupByChannel, data, 1000, byref(read), None)
        dat.write(str(i) + "\t" + str(k) + "\t" + str(np.average(data)) + "\n")
        print("Point: "+str(i0)+":"+str(j0))
        reverse.append(j0)
        j0+=1
    i0+=1
dat.close()
x,y,z= np.loadtxt(nm, delimiter='\t').T
yf=[y[i] for i in forward]
xf=[x[i] for i in forward]
zf=[z[i] for i in forward]
yb=[y[i] for i in reverse]
xb=[x[i] for i in reverse]
zb=[z[i] for i in reverse]
#za=[(zf[i]+zb[i])/2 for i in range(itrt*itrt)]
zt=np.asarray(zf)
zu=np.asarray(zb)
nrows=itrt
ncols=itrt
grid = zt.reshape((nrows, ncols))
plt.imshow(grid, extent=(min(xf), max(xf), max(yf), min(yf)))
plt.colorbar()
plt.show()
grid = zu.reshape((nrows, ncols))
plt.imshow(grid, extent=(min(xb), max(xb), max(yb), min(yb)))
