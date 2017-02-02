UUTrap v0.1

Software for monitoring an optical tweezer.
Structure of the program:

UUTrap: Main folder. Important executables should be placed here.
|
|--Model: Houses the files related to periferals, such as NI acquision cards, etc.
|
|--View: Houses everything related to visualization of data.
|
|--Controler: Houses the intermediate steps between model and View. It handles the conditioning of data before being presented to the user.
