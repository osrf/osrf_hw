EESchema Schematic File Version 2
LIBS:device
LIBS:OSCILLATOR
LIBS:connectors
LIBS:power
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
LIBS:cameras
LIBS:IMU
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 2
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
L LSM6DS3 U?
U 1 1 56671899
P 2000 2750
F 0 "U?" H 1750 3450 50  0000 C CNN
F 1 "ST_LSM6DS3" H 1650 2350 50  0000 C CNN
F 2 "Housings_LGA:LGA14_2.5X3X0.86" H 2000 2750 200 0001 C CNN
F 3 "http://www.st.com/web/en/resource/technical/document/datasheet/DM00133076.pdf" H 2000 2750 500 0001 C CNN
F 4 "STMicroelectronics" H 2000 2750 60  0001 C CNN "MFN"
F 5 "LSM6DS3TR" H 2000 2750 60  0001 C CNN "MFP"
F 6 "digikey" H 2000 2750 60  0001 C CNN "D1"
F 7 "mouser" H 2000 2750 60  0001 C CNN "D2"
F 8 "497-15383" H 2000 2750 60  0001 C CNN "D1PN"
F 9 "http://www.digikey.com/product-detail/en/LSM6DS3TR/497-15383-1-ND/5180534" H 2000 2750 60  0001 C CNN "D1PL"
F 10 "_" H 2000 2750 60  0001 C CNN "D2PN"
F 11 "_" H 2000 2750 60  0001 C CNN "D2PL"
F 12 "LGA14" H 2000 2750 60  0001 C CNN "Package"
F 13 "_" H 2000 2750 60  0000 C CNN "Description"
F 14 "_" H 2000 2750 60  0001 C CNN "Voltage"
F 15 "_" H 2000 2750 60  0001 C CNN "Power"
F 16 "_" H 2000 2750 60  0001 C CNN "Tolerance"
F 17 "_" H 2000 2750 60  0001 C CNN "Temperature"
F 18 "_" H 2000 2750 60  0001 C CNN "ReverseVoltage"
F 19 "_" H 2000 2750 60  0001 C CNN "ForwardVoltage"
F 20 "_" H 2000 2750 60  0001 C CNN "Cont.Current"
F 21 "_" H 2000 2750 60  0001 C CNN "Frequency"
F 22 "_" H 2000 2750 60  0001 C CNN "ResonnanceFreq"
	1    2000 2750
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 566718A0
P 2000 3250
F 0 "#PWR?" H 2000 3000 50  0001 C CNN
F 1 "GND" H 2000 3100 50  0000 C CNN
F 2 "" H 2000 3250 60  0000 C CNN
F 3 "" H 2000 3250 60  0000 C CNN
	1    2000 3250
	1    0    0    -1  
$EndComp
$Comp
L C C?
U 1 1 566718B9
P 1200 1950
F 0 "C?" H 1225 2050 50  0000 L CNN
F 1 "100n" H 1225 1850 50  0000 L CNN
F 2 "Dipoles_SMD:C_0402" H 1238 1800 50  0001 C CNN
F 3 "http://product.tdk.com/en/catalog/datasheets/mlcc_commercial_general_en.pdf" H 1200 1950 50  0001 C CNN
F 4 "TDK" H 1200 1950 50  0001 C CNN "MFN"
F 5 "C1005X5R0J104K050BA" H 1200 1950 50  0001 C CNN "MFP"
F 6 "digikey" H 1200 1950 50  0001 C CNN "D1"
F 7 "mouser" H 1200 1950 50  0001 C CNN "D2"
F 8 "445-1266" H 1200 1950 50  0001 C CNN "D1PN"
F 9 "http://www.digikey.com/product-detail/en/C1005X5R0J104K050BA/445-1266-1-ND/567731" H 1200 1950 50  0001 C CNN "D1PL"
F 10 "_" H 1200 1950 50  0001 C CNN "D2PN"
F 11 "_" H 1200 1950 50  0001 C CNN "D2PL"
F 12 "0402" H 1200 1950 50  0001 C CNN "Package"
F 13 "_" H 1200 1950 50  0000 C CNN "Description"
F 14 "6.3" H 1200 1950 50  0001 C CNN "Voltage"
F 15 "_" H 1200 1950 50  0001 C CNN "Power"
F 16 "10%" H 1200 1950 50  0001 C CNN "Tolerance"
F 17 "X5R" H 1200 1950 50  0001 C CNN "Temperature"
F 18 "_" H 1200 1950 50  0001 C CNN "ReverseVoltage"
F 19 "_" H 1200 1950 50  0001 C CNN "ForwardVoltage"
F 20 "_" H 1200 1950 50  0001 C CNN "Cont.Current"
F 21 "_" H 1200 1950 50  0001 C CNN "Frequency"
F 22 "_" H 1200 1950 50  0001 C CNN "ResonnanceFreq"
	1    1200 1950
	1    0    0    -1  
$EndComp
$Comp
L C C?
U 1 1 566718D3
P 1400 1950
F 0 "C?" H 1425 2050 50  0000 L CNN
F 1 "100n" H 1425 1850 50  0000 L CNN
F 2 "Dipoles_SMD:C_0402" H 1438 1800 50  0001 C CNN
F 3 "http://product.tdk.com/en/catalog/datasheets/mlcc_commercial_general_en.pdf" H 1400 1950 50  0001 C CNN
F 4 "TDK" H 1400 1950 50  0001 C CNN "MFN"
F 5 "C1005X5R0J104K050BA" H 1400 1950 50  0001 C CNN "MFP"
F 6 "digikey" H 1400 1950 50  0001 C CNN "D1"
F 7 "mouser" H 1400 1950 50  0001 C CNN "D2"
F 8 "445-1266" H 1400 1950 50  0001 C CNN "D1PN"
F 9 "http://www.digikey.com/product-detail/en/C1005X5R0J104K050BA/445-1266-1-ND/567731" H 1400 1950 50  0001 C CNN "D1PL"
F 10 "_" H 1400 1950 50  0001 C CNN "D2PN"
F 11 "_" H 1400 1950 50  0001 C CNN "D2PL"
F 12 "0402" H 1400 1950 50  0001 C CNN "Package"
F 13 "_" H 1400 1950 50  0000 C CNN "Description"
F 14 "6.3" H 1400 1950 50  0001 C CNN "Voltage"
F 15 "_" H 1400 1950 50  0001 C CNN "Power"
F 16 "10%" H 1400 1950 50  0001 C CNN "Tolerance"
F 17 "X5R" H 1400 1950 50  0001 C CNN "Temperature"
F 18 "_" H 1400 1950 50  0001 C CNN "ReverseVoltage"
F 19 "_" H 1400 1950 50  0001 C CNN "ForwardVoltage"
F 20 "_" H 1400 1950 50  0001 C CNN "Cont.Current"
F 21 "_" H 1400 1950 50  0001 C CNN "Frequency"
F 22 "_" H 1400 1950 50  0001 C CNN "ResonnanceFreq"
	1    1400 1950
	1    0    0    -1  
$EndComp
$Comp
L +1V8 #PWR?
U 1 1 566718DA
P 1350 1800
F 0 "#PWR?" H 1350 1650 50  0001 C CNN
F 1 "+1V8" H 1350 1940 50  0000 C CNN
F 2 "" H 1350 1800 60  0000 C CNN
F 3 "" H 1350 1800 60  0000 C CNN
	1    1350 1800
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 566718E0
P 1300 2100
F 0 "#PWR?" H 1300 1850 50  0001 C CNN
F 1 "GND" H 1300 1950 50  0000 C CNN
F 2 "" H 1300 2100 60  0000 C CNN
F 3 "" H 1300 2100 60  0000 C CNN
	1    1300 2100
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR?
U 1 1 566718E6
P 1350 2700
F 0 "#PWR?" H 1350 2450 50  0001 C CNN
F 1 "GND" H 1350 2550 50  0000 C CNN
F 2 "" H 1350 2700 60  0000 C CNN
F 3 "" H 1350 2700 60  0000 C CNN
	1    1350 2700
	1    0    0    -1  
$EndComp
Text GLabel 2500 2450 2    60   Input ~ 0
IMU_SS#
Text GLabel 1500 2350 0    60   Input ~ 0
IMU_INT1
Wire Wire Line
	2000 3250 2100 3250
Wire Wire Line
	1200 1800 1400 1800
Wire Wire Line
	2000 1950 2100 1950
Wire Wire Line
	2050 1800 2050 1950
Wire Wire Line
	1350 1800 2050 1800
Wire Wire Line
	1200 2100 1400 2100
Wire Wire Line
	1500 2650 1500 2750
Wire Wire Line
	1500 2700 1350 2700
Connection ~ 1350 1800
Connection ~ 2050 1950
Connection ~ 1300 2100
Connection ~ 1500 2700
NoConn ~ 2200 1950
NoConn ~ 1500 2850
Text GLabel 1500 2450 0    60   Input ~ 0
IMU_INT2
Text GLabel 1500 2550 0    60   Input ~ 0
IMU_MISO
Text GLabel 2500 2650 2    60   Input ~ 0
IMU_MOSI
Text GLabel 2500 2550 2    60   Input ~ 0
IMU_SCK
$EndSCHEMATC
