# UUTrap v0.1 #
This program is developed for monitoring an optical tweezer. Normally the tasks that need to be done are acquiring analog signals (QPD) and counters (APD). The program was built with a GUI that allows to monitor 3 analog signals (QPDx, QPDy, QPDz), and their variances. It also has a value monitor, which displays with big numbers the current value of the QPD and is useful for aligning purposes.

The GUI also allows a high time accuracy acquisition of the channels and computes the power spectrum. This is normally useful for calculating the trap stifness.

A configuration window enables the user to change the more important parameters of the experiment at runtime.

## Software for monitoring an optical tweezer. ##
The program follows the Model-View-Controller design structure. This allows a rapid exchange of different parts of the code.

For example, the acquisition card can be changed, and the only part of the program that needs to be updated is the Model. Conversely the GUI can be modified to suit the user needs just by updating the View. The Controller hosts the interfacing with real devices. New drivers can be loaded hearer provided that the function names and outputs are maintained. 


### Structure of the folders: ###
UUTrap: Main folder. Important executables should be placed here.

--Model: Houses the intermediate steps between model and View. It handles the conditioning of data before being presented to the user.

--View: Houses everything related to visualization of data.

--Controller: Houses the files related to periferals, such as NI acquision cards, etc.
