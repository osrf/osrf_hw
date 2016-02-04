EESchema Schematic File Version 2
LIBS:device
LIBS:OSCILLATOR
LIBS:usb_controller
LIBS:ADP50xx
LIBS:usb3_connector
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:lattice
LIBS:connectors
LIBS:altera
LIBS:power
LIBS:voltage_translators
LIBS:semtech
LIBS:i2c_flash
LIBS:generic_ic
LIBS:mt41k128m16
LIBS:artix7
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 9 11
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L GND #PWR076
U 1 1 56274B36
P 3900 3400
F 0 "#PWR076" H 3900 3150 50 0001 C CNN
F 1 "GND" H 3900 3250 50 0000 C CNN
F 2 "" H 3900 3400 60 0000 C CNN
F 3 "" H 3900 3400 60 0000 C CNN
 1 3900 3400
 1 0 0 -1 
$EndComp
$Comp
L GND #PWR077
U 1 1 5638C153
P 7750 3700
F 0 "#PWR077" H 7750 3450 50 0001 C CNN
F 1 "GND" H 7750 3550 50 0000 C CNN
F 2 "" H 7750 3700 60 0000 C CNN
F 3 "" H 7750 3700 60 0000 C CNN
 1 7750 3700
 1 0 0 -1 
$EndComp
$Comp
L Artix7-484 U6
U 6 1 56563BEC
P 6050 3200
F 0 "U6" H 6050 3200 50 0000 C CNN
F 1 "Artix7-484" H 6050 3100 50 0000 C CNN
F 2 "BGA:BGA484C100P22X22_2300X2300X185" H 6050 3200 50 0001 C CNN
F 3 "http://www.xilinx.com/support/documentation/data_sheets/ds181_Artix_7_Data_Sheet.pdf" H 6050 3200 50 0001 C CNN
F 4 "Xilinx" H 6050 3200 50 0001 C CNN "MFN"
F 5 "XC7A100T-1FGG484C" H 6050 3200 50 0001 C CNN "MFP"
F 6 "digikey" H 6050 3200 50 0001 C CNN "D1"
F 7 "mouser" H 6050 3200 50 0001 C CNN "D2"
F 8 "122-1885" H 6050 3200 50 0001 C CNN "D1PN"
F 9 "http://www.digikey.com/product-detail/en/XC7A100T-1FGG484C/122-1885-ND/3925804" H 6050 3200 50 0001 C CNN "D1PL"
F 10 "_" H 6050 3200 50 0001 C CNN "D2PN"
F 11 "_" H 6050 3200 50 0001 C CNN "D2PL"
F 12 "BGA484" H 6050 3200 50 0001 C CNN "Package"
F 13 "Xilinx Artix7 FPGA, 484pins, 100 000 cells" H 6050 3200 50 0001 C CNN "Description"
F 14 "_" H 6050 3200 50 0001 C CNN "Voltage"
F 15 "_" H 6050 3200 50 0001 C CNN "Power"
F 16 "_" H 6050 3200 50 0001 C CNN "Tolerance"
F 17 "_" H 6050 3200 50 0001 C CNN "Temperature"
F 18 "_" H 6050 3200 50 0001 C CNN "ReverseVoltage"
F 19 "_" H 6050 3200 50 0001 C CNN "ForwardVoltage"
F 20 "_" H 6050 3200 50 0001 C CNN "Cont.Current"
F 21 "_" H 6050 3200 50 0001 C CNN "Frequency"
F 22 "_" H 6050 3200 50 0001 C CNN "ResonnanceFreq"
 6 6050 3200
 1 0 0 -1 
$EndComp
Wire Wire Line
 4200 3500 4350 3500
Wire Wire Line
 3900 3400 4350 3400
Wire Wire Line
 4200 3300 4350 3300
Wire Wire Line
 4200 3100 4350 3100
Wire Wire Line
 4350 3000 4200 3000
Wire Wire Line
 4350 2900 4200 2900
Wire Wire Line
 4200 2800 4200 3500
Wire Wire Line
 4350 2800 4200 2800
Wire Wire Line
 4350 3200 4200 3200
Connection ~ 4200 3400
Connection ~ 4200 3300
Connection ~ 4200 3100
Connection ~ 4200 3000
Connection ~ 4200 2900
Connection ~ 4200 3200
NoConn ~ 7750 3300
NoConn ~ 7750 3400
NoConn ~ 7750 3500
NoConn ~ 7750 3600
NoConn ~ 4350 3700
NoConn ~ 4350 3800
NoConn ~ 7750 3000
NoConn ~ 7750 3100
NoConn ~ 7750 3200
NoConn ~ 7750 2800
NoConn ~ 4350 3600
NoConn ~ 7750 2900
$EndSCHEMATC
