#!/usr/bin/env python

from __future__ import print_function
import os
import argparse
import time
import sys
import csv
from collections import OrderedDict
import operator
#TODO Generate file using schlib.py class defnition
#TODO Define format of csv or create parser for each manufacturer 
#LIMITATIONS doesnt handle UFBGA like packages
#TODO Implement PLCC (not necessary, needed only for footprint generation)
#FIXME Think if PQFP and PLCC are supposed to be square chips
#add list of packages ? or just number of pins ? 
stringhelp = '### SCH NUMEROTATION TYPES ###                                       \n'\
'   ######## ONE SIDE ########                                             \n'\
'                                                                          \n'\
'      SIL          SIL-ALT                                                \n'\
'       ___           ___                                                  \n'\
'   1 --|  |       1--|  |                                                 \n'\
'   2 --|  |   N/2+1--|  |                                                 \n'\
'   3 --|  |       2--|  |                                                 \n'\
'   . --|  |   N/2+2--|  |                                                 \n'\
'   . --|  |     ...--|  |                                                 \n'\
'   . --|  |     N/2--|  |                                                 \n'\
'   N --|__|       N--|__|                                                 \n'\
'                                                                          \n'\
'                                                                          \n'\
'  ######## TWO SIDES ########                                             \n'\
'                                                                          \n'\
'        DIL                   CONN1             CONN2                     \n'\
'       _____                  _____             _____                     \n'\
'   1 --|    |--N          1 --|    |--2     1 --|    |--N/2+1             \n'\
'   2 --|    |--           3 --|    |--4     2 --|    |--N/2+2             \n'\
'   3 --|    |--^          . --|    |--      3 --|    |--                  \n'\
'   . --|    |--.          . --|    |--.     . --|    |--.                 \n'\
'   . --|    |--.          . --|    |--.     . --|    |--.                 \n'\
'   . --|    |--N/2+2      . --|    |--.     . --|    |--.                 \n'\
'  N/2--|____|--N/2+1     N-1--|____|--N    N/2--|____|--N                 \n'\
'                                                                          \n'\
'                                                                          \n'\
'  ######### FOUR SIDES #########                                          \n'\
'                                                                          \n'\
'              PLCC                                PQFP                    \n'\
'              <--     <--                       <--     <--               \n'\
'       __|_|_|_|_|_|_|_|_                __|_|_|_|_|_|_|_|_               \n'\
'     --|                 |--          1--|o                |--            \n'\
'     --|                 |--          2--|                 |--            \n'\
'     --|                 |-- ^        3--|                 |-- ^          \n'\
'     --|                 |-- |         --|                 |-- |          \n'\
'    1--|o                |--           --|                 |--            \n'\
'    2--|                 |--           --|                 |--            \n'\
'    3--|                 |--           --|                 |--            \n'\
'     --|                 |-- ^         --|                 |-- ^          \n'\
'     --|_________________|-- |         --|_________________|-- |          \n'\
'         | | | | | | | |                   | | | | | | | |                \n'\
'           -->      -->                      -->      -->                 \n'\
'                                                                          \n'\
'  ############ BGA #############                                          \n'\
'       1 2 3 4 ....                                                       \n'\
'      ___________________________                                         \n'\
'    A|o o o o o o o o o o o o o o| ^                                      \n'\
'    B|o o o o o o o o o o o o o o| |                                      \n'\
'    C|o o o o o o o o o o o o o o| |                                      \n'\
'    .|o o o o o o o o o o o o o o| |                                      \n'\
'    .|o o o o o <------>o o o o o| |                                      \n'\
'    .|o o o o o ^ NIntw o o o o o| |           ==> BGA Represented as PQFP\n'\
'     |o o o o o |       o o o o o| |  height                              \n'\
'     |o o o o o |NInth  o o o o o| |                                      \n'\
'     |o o o o o |       o o o o o| |                                      \n'\
'     |o o o o o ^       o o o o o| |                                      \n'\
'     |o o o o o o o o o o o o o o| |                                      \n'\
'     |o o o o o o o o o o o o o o| |                                      \n'\
'     |o o o o o o o o o o o o o o| |                                      \n'\
'     |___________________________| |                                      \n'\
'               width               ^                                      \n'\
'     <---------------------------->                                       \n'\
'  usage: ./generate_component.py ConfigFile.txt                           \n'

print(stringhelp)
if len(sys.argv) >1:
    infile = sys.argv[1]
else:
    print('please provide a configuration file')
    sys.exit()
################################
##### Function declaration #####
################################

def importCSV(filename,pinOrder):
# expected csv format: 
# PIN_NAME,PIN_NUMBER
    if not os.path.isfile(filename):
        print('pinfile not found')
        return
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        pinDict = {rows[1]:rows[0] for rows in reader}
    if pinOrder == 'BYNAME':
        sortedDico = OrderedDict(sorted(pinDict.items(), key=operator.itemgetter(1)))
#        print(sortedDico)
        return sortedDico
    else:
        return pinDict
def correctModulo(table):
    for r in table:
        if r%100 != 0:
            r -= r%100
    return table

def rectCorners(NbPin, nbside, step):#, stepy, initoffsetx, initoffsety):
# return coordinate of top-left and bottom-right corner of the schematic rectangle
    res = []
    if nbside==1:
        res = [-step,-(step + NbPin/2*step), step, step + NbPin/2*step]
        res = correctModulo(res)
    elif nbside == 2:
            res = [-2*step,-NbPin/4*step-step,2*step,NbPin/4*step+step]
            res = correctModulo(res)
    elif nbside == 4:
        res = [-(2*step+NbPin/8*step), -(2*step+NbPin/8*step),\
                2*step+NbPin/8*step, 2*step+NbPin/8*step]
        res = correctModulo(res)
    return res
        
#checks if the pin exist in the dictionary, if not the pin will be named:\
# PIN_"PIN_NUMBER" for example A5 will be named PIN_A5
def checkPinListSorted(index,typec='OTHER'):
    if usePinList ==1:
        try:
            pinPair = pinDico.items()[index-1] 
            pinName = pinPair[1]

            pinNumber = pinPair[0]
            return str(pinName) + ' ' + str(pinNumber)
        except IndexError:
            pass
    if typec == 'BGA':
        return ''
    pinName = dictParameters['PinFormat'] + str(index)
    return pinName + ' ' + str(index)

def checkPinList(pinNumberStr):
    if usePinList ==1:
        try:
            pinName = pinDico[pinNumberStr]
            return pinName
        except KeyError:
            pass
    pinName = 'PIN_' + pinNumberStr
    return pinName   
###############################################
##### Variable declaration/initialization #####
###############################################
if not os.path.isfile(infile) or infile == '':
    print('ERROR: config file doesnt exist')
    sys.exit()
dictParameters=OrderedDict([
('nbSide','1'),
('chiptype','OTHER'),
('pinOrder','NAME'),
('height','0'),
('width','0'),
('NInth','0'),
('NIntw','0'),
('PinoutFile',''),
('outLibrary',''),
('name',''),
('alias',''),
('prefix','U'),
('datasheet',''),
('keywords',''),
('footprintFormat',''),
('PinFormat','PIN_'),
('MFN','_'),
('MFP','_'),
('D1PN','_'),
('D1PL','_'),
('D2PN','_'),
('D2PL','_'),
('Package','_'),
('Description','_'),
('Voltage','_'),
('Power','_'),
('Tolerance','_'),
('Temperature','_'),
('ReverseVoltage','_'),
('ForwardVoltage','_'),
('Cont.Current','_'),
('Frequency','_'),
('ResonnanceFreq','_')
])
whitelist = ['PinFormat']
with open(infile,'r+') as inf:
    while True:
        line = inf.readline()
        line = line.replace('\n','')
        if not line: break
        lsplit = line.split('=')
        if lsplit[0] in dictParameters:
                if (lsplit[1] != '' and lsplit[1]!= dictParameters[lsplit[0]]) or lsplit[0] in whitelist:
                    dictParameters[lsplit[0]]=lsplit[1]

#check incoherences
# between order and sides
if dictParameters['chiptype'] != 'BGA':
    if dictParameters['pinOrder'] != 'BYNAME':
        if dictParameters['pinOrder'] == 'SIL' or dictParameters['pinOrder'] == 'SIL-ALT':
            dictParameters['nbSide'] = '1'
        elif dictParameters['pinOrder'] == 'CONN1' or dictParameters['pinOrder'] == 'CONN2' or dictParameters['pinOrder'] == 'DIL':
            dictParameters['nbSide'] = '2'
        elif dictParameters['pinOrder'] == 'PLCC' or dictParameters['pinOrder'] == 'PQFP':
            dictParameters['nbSide'] = '4'
# between sides and NPin
if dictParameters['chiptype'] == 'BGA':
    NPin = int(dictParameters['height'])*int(dictParameters['width']) - int(dictParameters['NIntw'])*int(dictParameters['NIntw'])
else:
    if dictParameters['width'] > 2:
        NPin = 2 * int(dictParameters['height']) + 2*(int(dictParameters['width'])-2)
    elif dictParameters['width'] == 2:
        NPin = 2 * int(dictParameters['height'])
    else:
        NPin = int(dictParameters['height'])
#print(NPin)
#Not existing letters in BGA naming: I,O,Q,S,X,Z,
BGAdico=['A','B','C','D','E','F','G','H','J','K','L','M','N','P','R','T','U','V',\
        'W','Y','AA','AB','AC','AD','AE','AF','AG','AH','AJ','AK']
length = 200
typePin = 'U'
textSize = 50
step = 200
stdString = '" 0 0 50 H I C C'
[rectxmin,rectymin,rectxmax,rectymax]=rectCorners(NPin,int(dictParameters['nbSide']),step)

outstring = 'EESchema-LIBRARY Version 2.2 Date: ' + time.strftime("%d/%m/%Y") + '-' + time.strftime('%H:%M:%S') + '\n'
outstring += '#encoding utf-8\n#\n# ' + dictParameters['name'] + '\n#\nDEF '
outstring += dictParameters['name'] + ' U 0 40 Y Y 1 F N\n'
outstring += 'F0 "' + dictParameters['prefix'] + '" ' + str(rectxmin) + ' ' + str(rectymax+2*textSize) + ' 50 H V C C\n'
outstring += 'F1 "' + dictParameters['name'] + '" ' + str(rectxmin) + ' ' + str(rectymin - 2*textSize) + ' 50 H V C C\n'
outstring += 'F2 "_'+ stdString +'\n'
outstring += 'F3 "' + dictParameters['datasheet'] + stdString + '\n'
outstring += 'F4 "' + dictParameters['MFN'] + stdString + ' "MFN"\n'
outstring += 'F5 "' + dictParameters['MFP'] + stdString + ' "MFP"\n'
outstring += 'F6 "digikey' + stdString + ' "D1"\n'
outstring += 'F7 "mouser' + stdString + ' "D2"\n'
i=0
for key in dictParameters:
#17 = index of D1PN
    if(i>len(dictParameters)-16):
        outstring += 'F'+str(i-10)+' "' + dictParameters[key] + stdString + ' "' + key + '"\n'
    i+=1

# Add Alias
if dictParameters['alias'] != '':
    outstring += 'ALIAS ' + dictParameters['alias'] + '\n'
# Add footprint list
if dictParameters['footprintFormat'] != '':
    outstring += '$FPLIST\n'
    for elt in dictParameters['footprintFormat'].split(','):
        if elt !='':
            outstring += ' ' + elt + '\n'
    outstring += '$ENDFPLIST\n'

outstring += 'DRAW\n'
outstring += 'S '+str(rectxmin)+' '+str(rectymin)+' '+str(rectxmax)+' '\
             +str(rectymax)+ ' 0 1 0 f\n'

# import pins from provided CSV file
usePinList = 0
if dictParameters['PinoutFile'] != '' and os.path.isfile(dictParameters['PinoutFile']):
    pinDico = importCSV(dictParameters['PinoutFile'],dictParameters['pinOrder']) 
    if len(pinDico) != 0:
        usePinList = 1

# Check if chip is a BallArray or a regular chip
halfNpin = NPin/2
if dictParameters['chiptype'] == 'BGA':
    if int(dictParameters['width'])>30 or int(dictParameters['height'])>30:
        print('BGA dimension cannot exceed 30 balls per side (900 pins)')
        sys.exit(0)
#    Npin = int(dictParameters['height'])*int(dictParameters['width']) - int(dictParameters['NIntw'])*int(dictParameters['NIntw'])
    index = 0; iforbidmin=0;iforbidmax=0;jforbidmin=0;jforbidmax=0;
    if(int(dictParameters['NIntw']) != 0 and int(dictParameters['NInth']) != 0):
        iforbidmin = (int(dictParameters['height'])-int(dictParameters['NInth']))/2
        iforbidmax = int(dictParameters['height']) - iforbidmin + int(dictParameters['NInth'])/2
        jforbidmin = (int(dictParameters['width'])-int(dictParameters['NIntw']))/2
        jforbidmax = int(dictParameters['width']) - jforbidmin + int(dictParameters['NIntw'])/2
    quarterNpin = NPin/4
    threeQuartNpin = 3*quarterNpin
    for i in range(int(dictParameters['height'])):
        for j in range(int(dictParameters['width'])):
            # skip center balls if needed
            if(not(i > iforbidmin and i < iforbidmax and j > jforbidmin and j < jforbidmax)):
                index += 1
                string = BGAdico[i]+str(j+1)
                if dictParameters['nbSide'] == '1':
                    print('only 2 and 4 sides supported for BGA components')
                    sys.exit(0)
                elif dictParameters['nbSide'] == '2':
                    if index <= halfNpin:
                        posx = rectxmin - length
                        posy = rectymin + step + (halfNpin-index) * step
                        side = 'R'
                    else:
                        posx = rectxmax + length
                        posy = rectymin + step + (index-halfNpin-1) * step
                        side = 'L'
                elif dictParameters['nbSide'] == '4':
                    if index <= quarterNpin:
                        side = 'R'
                        posx = rectxmin - length
                        posy = rectymin + 2*step + (quarterNpin-index+1)*step
                    elif index <= halfNpin:
                        side = 'U'
                        posx = rectxmin + 2*step + ((index-quarterNpin))*step
                        posy = rectymin - length
                    elif index <= threeQuartNpin:
                        side = 'L'
                        posx = rectxmax + length
                        posy = rectymin + 2*step + (index-halfNpin)*step
                    else:
                        side = 'D'
                        posx = rectxmin + 2*step + (NPin-(index))*step
                        posy = rectymax + length
                if dictParameters['pinOrder']=='BYNAME':
                    pinPairStr = checkPinListSorted(index,'BGA')
                    if pinPairStr == '':
                        pinPairStr = checkPinList(string) + ' ' + string
                else:
                    pinPairStr = checkPinList(string) + ' ' + string
    
                outstring += 'X '+ pinPairStr + ' ' + str(posx) + ' ' +\
                            str(posy) + ' ' + str(length)\
                            + ' ' + side + ' ' + str(textSize) + ' ' + \
                            str(textSize) + ' 1 1 ' + typePin + '\n'

elif dictParameters['chiptype'] == 'OTHER':
    print('in OTHER case: "' + dictParameters['nbSide'] + '"')

    side = 'R'
    if dictParameters['nbSide'] == '1':
        print('\n\n1side\n')
        for i in range(NPin):
            if dictParameters['pinOrder']=='BYNAME':
                pinPairStr = checkPinListSorted(i+1)
            elif dictParameters['pinOrder'] == 'SIL':
                    pinPairStr = checkPinList(str(i+1))+ ' ' + str(i+1) 
            elif dictParameters['pinOrder'] == 'SIL-ALT':
                if i%2==0:
                    pinPairStr = checkPinList(str(i/2+1)) + ' ' + str(i/2+1)
                else:
                    pinPairStr = checkPinList(str((NPin+i)/2+1)) + ' ' + str((NPin+i)/2+1)

            else:
                print('error your pinorder doesnt match number os sides')
                sys.exit()
            outstring += 'X '+ pinPairStr+ ' ' + str(rectxmin - \
                        length) + ' ' + str(rectymin + step + \
                        (NPin-i)*step) + ' ' + str(length) + ' ' +\
                        side + ' ' + str(textSize) + ' ' + \
                        str(textSize) + ' 1 1 ' + typePin + '\n'
                
    elif dictParameters['nbSide'] == '2':
        print('\n\n2sides\n')
        if dictParameters['pinOrder']=='BYNAME':
            for i in range(NPin):
                pinPairStr = checkPinListSorted(i+1)
                if i < int(dictParameters['height']):
                    posx = rectxmin - length
                    posy = rectymin + step + (halfNpin-i) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + (i-halfNpin+1) * step
                    side = 'L'
                outstring += 'X '+ pinPairStr\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(textSize)\
                            + ' ' + str(textSize) + ' 1 1 ' + typePin\
                            + '\n'
        elif dictParameters['pinOrder'] == 'CONN2':
            for i in range(NPin):
                if i < int(dictParameters['height']):
                    posx = rectxmin - length
                    posy = rectymin + step + (halfNpin-i) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + (NPin-i) * step
                    side = 'L'
                outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(textSize)\
                            + ' ' + str(textSize) + ' 1 1 ' + typePin\
                            + '\n'
    
        elif dictParameters['pinOrder'] == 'CONN1':
            for i in range(NPin):
                if i%2 ==0:
                    posx = rectxmin - length
                    posy = rectymin + step + ((NPin-i)/2-1) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + ((NPin-i)/2) * step
                    side = 'L'
                outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(textSize)\
                            + ' ' + str(textSize) + ' 1 1 ' + typePin\
                            + '\n'
    
        elif dictParameters['pinOrder'] == 'DIL':
            for i in range(NPin):
                if i < halfNpin:
                    posx = rectxmin - length
                    posy = rectymin + step + (halfNpin-i) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + (i-halfNpin+1) * step
                    side = 'L'
                outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(textSize)\
                            + ' ' + str(textSize) + ' 1 1 ' + typePin\
                            + '\n'
            
    ### Four sides schematics ###
    elif dictParameters['nbSide'] == '4':
        quarterNpin = NPin/4
        threeQuartNpin = 3*quarterNpin
        for i in range(NPin):
            if i < quarterNpin:
                side = 'R'
                posx = rectxmin - length
                posy = rectymin + step + (quarterNpin-i)*step
            elif i < halfNpin:
                side = 'U'
                posx = rectxmin + step + ((i+1-quarterNpin))*step
                posy = rectymin - length
            elif i< threeQuartNpin:
                side = 'L'
                posx = rectxmax + length
                posy = rectymin + step + (i+1-halfNpin)*step
            else:
                side = 'D'
                posx = rectxmin + step + (NPin-(i-1))*step
                posy = rectymax + length
            if dictParameters['pinOrder']=='BYNAME':
                pinPairStr = checkPinListSorted(i+1)
            elif dictParameters['pinOrder'] == 'PQFP':
                pinPairStr = checkPinList(str(i+1)) + ' ' + str(i+1)
     
            elif dictParameters['pinOrder'] == 'PLCC':
                print('PLCC not implemented yet sorry')
                exit(0)
            else:
                print('order not compatible with number of sides provided')
                exit(0)
                
            outstring += 'X '+ pinPairStr + ' ' + str(posx) + ' ' + str(posy) + ' '\
                        + str(length) + ' ' + side + ' ' + str(textSize) + ' ' + \
                        str(textSize) + ' 1 1 ' + typePin + '\n'
    else:
        print('wrong nbSide')
else:
    print('unknown package type')
    sys.exit(0)

destLib = ''
if dictParameters['outLibrary']!='' and dictParameters['outLibrary'].endswith('.lib'):
    if os.path.isfile(dictParameters['outLibrary']):
        print('part will be added to ' +dictParameters['outLibrary'] + ' library')
        destLib = dictParameters['outLibrary']
        fileout = dictParameters['outLibrary'][:-4]+ 'temp'
    else:
        print('creating a new library: ' + dictParameters['outLibrary'])
        fileout = dictParameters['outLibrary'][:-4]
else:
    fileout = dictParameters['name']
    print('creating a new library: ' + fileout)
print(fileout)
docstring = 'EESchema-DOCLIB Version 2.0\n#\n$CMP '+dictParameters['name']+'\n'
docstring += 'D ' + dictParameters['Description'] + '\n'
docstring += 'K ' + dictParameters['keywords'] + '\n'
docstring += 'F ' + dictParameters['datasheet'] + '\n'
docstring += '$ENDCMP\n#\n#End Doc Library'

with open(fileout+'.dcm','w+') as docfile:
   docfile.write(docstring) 

with open(fileout+'.lib', 'w+') as outfile:
    outstring += 'ENDDRAW\nENDDEF\n#\n#End Library'
    outfile.write(outstring)

if destLib !='':
#    os.system('python '+os.path.join(os.getcwd(),'move_part.py') + ' ' + dictParameters['name'] + ' ' + fileout+'.lib' + ' ' + destLib )
    os.system('move_part.py' + ' ' + dictParameters['name'] + ' ' + fileout+'.lib' + ' ' + destLib )
    os.remove(fileout+'.lib')
    os.remove(fileout+'.dcm')
