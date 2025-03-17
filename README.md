# README

This repository contains code used to demonstrate a voltage glitch attack on a Arduino Nano Every.


## Fault Injection Demonstration

### Prerequisites

1. Desolder decoupling capacitors on Arduino development kit.
    - C2, C3, C4, C6, C8, C9, C10
    - **Note**: Removing C6 removes the option to program using USB.
2. Program FPGA DE10-Lite board by connecting USB, and flash the .sof file to the board.
    - To flash, use quartus programmer.

## FPGA code
All FPGA related code is found in the `fpga` folder.
There is a python script located in `fpga/uart_regs-1.0.4` that can be used to generate
UART vhdl modules and a python script that can be used to communicate with the UART modules.
This script generates files that are found in `fpga/generated`. If there is interest in 
adding more registers that are accessible over UART. Use the script, remember to include
the registers that are already generated. See any of the files found in the `fpga/generated`
folder to see the previously ran command.

Remember to run the command from the `fpga` folder.


## Simulations
Simulations of the system can be found in the `sim` folder.
The simulations are made using LTSpice and is only using default components.



## Schematic
Schematic and PCB has been designed using KiCad. See the `schematic` folder for the 
KiCad project files.


## Create Package


## License agreements

- MIT License for main project
    - License file: `./LICENSE`
- MIT License provided by VHDLwhiz for uart_regs tool.
    - License file: `./fpga/uart_regs-1.0.4/LICENSE.txt`
