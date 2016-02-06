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

def import_csv(filename,pin_order):
# expected csv format: 
# PIN_NAME,PIN_NUMBER
    if not os.path.isfile(filename):
        print('pinfile not found')
        return
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        pin_dict = {rows[1]:rows[0] for rows in reader}
    if pin_order == 'BYNAME':
        sorted_dico = OrderedDict(sorted(pin_dict.items(), key=operator.itemgetter(1)))
#        print(sorted_dico)
        return sorted_dico
    else:
        return pin_dict
def correct_modulo(table):
    for r in table:
        if r%100 != 0:
            r -= r%100
    return table

def rect_corners(nb_pins, nbside, step):#, stepy, initoffsetx, initoffsety):
# return coordinate of top-left and bottom-right corner of the schematic rectangle
    res = []
    if nbside==1:
        res = [-step,-(step + nb_pins/2*step), step, step + nb_pins/2*step]
        res = correct_modulo(res)
    elif nbside == 2:
            res = [-2*step,-nb_pins/4*step-step,2*step,nb_pins/4*step+step]
            res = correct_modulo(res)
    elif nbside == 4:
        res = [-(2*step+nb_pins/8*step), -(2*step+nb_pins/8*step),\
                2*step+nb_pins/8*step, 2*step+nb_pins/8*step]
        res = correct_modulo(res)
    return res
        
#checks if the pin exist in the dictionary, if not the pin will be named:\
# PIN_"PIN_NUMBER" for example A5 will be named PIN_A5
def check_pin_list_sorted(index,typec='OTHER'):
    if use_pin_list == 1:
        try:
            pin_pair = pin_dico.items()[index-1] 
            pin_name = pin_pair[1]

            pin_number = pin_pair[0]
            return str(pin_name) + ' ' + str(pin_number)
        except IndexError:
            pass
    if typec == 'BGA':
        return ''
    pin_name = dict_parameters['PinFormat'] + str(index)
    return pin_name + ' ' + str(index)

def checkPinList(pin_number_str):
    if use_pin_list ==1:
        try:
            pin_name = pin_dico[pin_number_str]
            return pin_name
        except KeyError:
            pass
    pin_name = 'PIN_' + pin_number_str
    return pin_name   
###############################################
##### Variable declaration/initialization #####
###############################################
if not os.path.isfile(infile) or infile == '':
    print('ERROR: config file doesnt exist')
    sys.exit()
dict_parameters=OrderedDict([
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
        if lsplit[0] in dict_parameters:
                if (lsplit[1] != '' and lsplit[1]!= dict_parameters[lsplit[0]]) or lsplit[0] in whitelist:
                    dict_parameters[lsplit[0]]=lsplit[1]

#check incoherences
# between order and sides
if dict_parameters['chiptype'] != 'BGA':
    if dict_parameters['pinOrder'] != 'BYNAME':
        if dict_parameters['pinOrder'] == 'SIL' or dict_parameters['pinOrder'] == 'SIL-ALT':
            dict_parameters['nbSide'] = '1'
        elif dict_parameters['pinOrder'] == 'CONN1' or dict_parameters['pinOrder'] == 'CONN2' or dict_parameters['pinOrder'] == 'DIL':
            dict_parameters['nbSide'] = '2'
        elif dict_parameters['pinOrder'] == 'PLCC' or dict_parameters['pinOrder'] == 'PQFP':
            dict_parameters['nbSide'] = '4'
# between sides and npin
if dict_parameters['chiptype'] == 'BGA':
    npin = int(dict_parameters['height'])*int(dict_parameters['width']) - int(dict_parameters['NIntw'])*int(dict_parameters['NIntw'])
else:
    if dict_parameters['width'] > 2:
        npin = 2 * int(dict_parameters['height']) + 2*(int(dict_parameters['width'])-2)
    elif dict_parameters['width'] == 2:
        npin = 2 * int(dict_parameters['height'])
    else:
        npin = int(dict_parameters['height'])
#print(npin)
#Not existing letters in BGA naming: I,O,Q,S,X,Z,
BGAdico=['A','B','C','D','E','F','G','H','J','K','L','M','N','P','R','T','U','V',\
        'W','Y','AA','AB','AC','AD','AE','AF','AG','AH','AJ','AK']
length = 200
type_pin = 'U'
text_size = 50
step = 200
std_string = '" 0 0 50 H I C C'
[rectxmin,rectymin,rectxmax,rectymax]=rect_corners(npin,int(dict_parameters['nbSide']),step)

outstring = 'EESchema-LIBRARY Version 2.2 Date: ' + time.strftime("%d/%m/%Y") + '-' + time.strftime('%H:%M:%S') + '\n'
outstring += '#encoding utf-8\n#\n# ' + dict_parameters['name'] + '\n#\nDEF '
outstring += dict_parameters['name'] + ' U 0 40 Y Y 1 F N\n'
outstring += 'F0 "' + dict_parameters['prefix'] + '" ' + str(rectxmin) + ' ' + str(rectymax+2*text_size) + ' 50 H V C C\n'
outstring += 'F1 "' + dict_parameters['name'] + '" ' + str(rectxmin) + ' ' + str(rectymin - 2*text_size) + ' 50 H V C C\n'
outstring += 'F2 "_'+ std_string +'\n'
outstring += 'F3 "' + dict_parameters['datasheet'] + std_string + '\n'
outstring += 'F4 "' + dict_parameters['MFN'] + std_string + ' "MFN"\n'
outstring += 'F5 "' + dict_parameters['MFP'] + std_string + ' "MFP"\n'
outstring += 'F6 "digikey' + std_string + ' "D1"\n'
outstring += 'F7 "mouser' + std_string + ' "D2"\n'
i=0
for key in dict_parameters:
#17 = index of D1PN
    if(i>len(dict_parameters)-16):
        outstring += 'F'+str(i-10)+' "' + dict_parameters[key] + std_string + ' "' + key + '"\n'
    i+=1

# Add Alias
if dict_parameters['alias'] != '':
    outstring += 'ALIAS ' + dict_parameters['alias'] + '\n'
# Add footprint list
if dict_parameters['footprintFormat'] != '':
    outstring += '$FPLIST\n'
    for elt in dict_parameters['footprintFormat'].split(','):
        if elt !='':
            outstring += ' ' + elt + '\n'
    outstring += '$ENDFPLIST\n'

outstring += 'DRAW\n'
outstring += 'S '+str(rectxmin)+' '+str(rectymin)+' '+str(rectxmax)+' '\
             +str(rectymax)+ ' 0 1 0 f\n'

# import pins from provided CSV file
use_pin_list = 0
if dict_parameters['PinoutFile'] != '' and os.path.isfile(dict_parameters['PinoutFile']):
    pin_dico = import_csv(dict_parameters['PinoutFile'],dict_parameters['pinOrder']) 
    if len(pin_dico) != 0:
        use_pin_list = 1

# Check if chip is a BallArray or a regular chip
half_npin = npin/2
if dict_parameters['chiptype'] == 'BGA':
    if int(dict_parameters['width'])>30 or int(dict_parameters['height'])>30:
        print('BGA dimension cannot exceed 30 balls per side (900 pins)')
        sys.exit(0)
#    Npin = int(dict_parameters['height'])*int(dict_parameters['width']) - int(dict_parameters['NIntw'])*int(dict_parameters['NIntw'])
    index = 0; iforbidmin=0;iforbidmax=0;jforbidmin=0;jforbidmax=0;
    if(int(dict_parameters['NIntw']) != 0 and int(dict_parameters['NInth']) != 0):
        iforbidmin = (int(dict_parameters['height'])-int(dict_parameters['NInth']))/2
        iforbidmax = int(dict_parameters['height']) - iforbidmin + int(dict_parameters['NInth'])/2
        jforbidmin = (int(dict_parameters['width'])-int(dict_parameters['NIntw']))/2
        jforbidmax = int(dict_parameters['width']) - jforbidmin + int(dict_parameters['NIntw'])/2
    quarter_npin = npin/4
    three_quart_npin = 3*quarter_npin
    for i in range(int(dict_parameters['height'])):
        for j in range(int(dict_parameters['width'])):
            # skip center balls if needed
            if(not(i > iforbidmin and i < iforbidmax and j > jforbidmin and j < jforbidmax)):
                index += 1
                string = BGAdico[i]+str(j+1)
                if dict_parameters['nbSide'] == '1':
                    print('only 2 and 4 sides supported for BGA components')
                    sys.exit(0)
                elif dict_parameters['nbSide'] == '2':
                    if index <= half_npin:
                        posx = rectxmin - length
                        posy = rectymin + step + (half_npin-index) * step
                        side = 'R'
                    else:
                        posx = rectxmax + length
                        posy = rectymin + step + (index-half_npin-1) * step
                        side = 'L'
                elif dict_parameters['nbSide'] == '4':
                    if index <= quarter_npin:
                        side = 'R'
                        posx = rectxmin - length
                        posy = rectymin + 2*step + (quarter_npin-index+1)*step
                    elif index <= half_npin:
                        side = 'U'
                        posx = rectxmin + 2*step + ((index-quarter_npin))*step
                        posy = rectymin - length
                    elif index <= three_quart_npin:
                        side = 'L'
                        posx = rectxmax + length
                        posy = rectymin + 2*step + (index-half_npin)*step
                    else:
                        side = 'D'
                        posx = rectxmin + 2*step + (npin-(index))*step
                        posy = rectymax + length
                if dict_parameters['pinOrder']=='BYNAME':
                    pin_pair_str = check_pin_list_sorted(index,'BGA')
                    if pin_pair_str == '':
                        pin_pair_str = checkPinList(string) + ' ' + string
                else:
                    pin_pair_str = checkPinList(string) + ' ' + string
    
                outstring += 'X '+ pin_pair_str + ' ' + str(posx) + ' ' +\
                            str(posy) + ' ' + str(length)\
                            + ' ' + side + ' ' + str(text_size) + ' ' + \
                            str(text_size) + ' 1 1 ' + type_pin + '\n'

elif dict_parameters['chiptype'] == 'OTHER':
    print('in OTHER case: "' + dict_parameters['nbSide'] + '"')

    side = 'R'
    if dict_parameters['nbSide'] == '1':
        print('\n\n1side\n')
        for i in range(npin):
            if dict_parameters['pinOrder']=='BYNAME':
                pin_pair_str = check_pin_list_sorted(i+1)
            elif dict_parameters['pinOrder'] == 'SIL':
                    pin_pair_str = checkPinList(str(i+1))+ ' ' + str(i+1) 
            elif dict_parameters['pinOrder'] == 'SIL-ALT':
                if i%2==0:
                    pin_pair_str = checkPinList(str(i/2+1)) + ' ' + str(i/2+1)
                else:
                    pin_pair_str = checkPinList(str((npin+i)/2+1)) + ' ' + str((npin+i)/2+1)

            else:
                print('error your pinorder doesnt match number os sides')
                sys.exit()
            outstring += 'X '+ pin_pair_str+ ' ' + str(rectxmin - \
                        length) + ' ' + str(rectymin + step + \
                        (npin-i)*step) + ' ' + str(length) + ' ' +\
                        side + ' ' + str(text_size) + ' ' + \
                        str(text_size) + ' 1 1 ' + type_pin + '\n'
                
    elif dict_parameters['nbSide'] == '2':
        print('\n\n2sides\n')
        if dict_parameters['pinOrder']=='BYNAME':
            for i in range(npin):
                pin_pair_str = check_pin_list_sorted(i+1)
                if i < int(dict_parameters['height']):
                    posx = rectxmin - length
                    posy = rectymin + step + (half_npin-i) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + (i-half_npin+1) * step
                    side = 'L'
                outstring += 'X '+ pin_pair_str\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(text_size)\
                            + ' ' + str(text_size) + ' 1 1 ' + type_pin\
                            + '\n'
        elif dict_parameters['pinOrder'] == 'CONN2':
            for i in range(npin):
                if i < int(dict_parameters['height']):
                    posx = rectxmin - length
                    posy = rectymin + step + (half_npin-i) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + (npin-i) * step
                    side = 'L'
                outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(text_size)\
                            + ' ' + str(text_size) + ' 1 1 ' + type_pin\
                            + '\n'
    
        elif dict_parameters['pinOrder'] == 'CONN1':
            for i in range(npin):
                if i%2 ==0:
                    posx = rectxmin - length
                    posy = rectymin + step + ((npin-i)/2-1) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + ((npin-i)/2) * step
                    side = 'L'
                outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(text_size)\
                            + ' ' + str(text_size) + ' 1 1 ' + type_pin\
                            + '\n'
    
        elif dict_parameters['pinOrder'] == 'DIL':
            for i in range(npin):
                if i < half_npin:
                    posx = rectxmin - length
                    posy = rectymin + step + (half_npin-i) * step
                    side = 'R'
                else:
                    posx = rectxmax + length
                    posy = rectymin + step + (i-half_npin+1) * step
                    side = 'L'
                outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                            str(length) + ' ' + side + ' ' + str(text_size)\
                            + ' ' + str(text_size) + ' 1 1 ' + type_pin\
                            + '\n'
            
    ### Four sides schematics ###
    elif dict_parameters['nbSide'] == '4':
        quarter_npin = npin/4
        three_quart_npin = 3*quarter_npin
        for i in range(npin):
            if i < quarter_npin:
                side = 'R'
                posx = rectxmin - length
                posy = rectymin + step + (quarter_npin-i)*step
            elif i < half_npin:
                side = 'U'
                posx = rectxmin + step + ((i+1-quarter_npin))*step
                posy = rectymin - length
            elif i< three_quart_npin:
                side = 'L'
                posx = rectxmax + length
                posy = rectymin + step + (i+1-half_npin)*step
            else:
                side = 'D'
                posx = rectxmin + step + (npin-(i-1))*step
                posy = rectymax + length
            if dict_parameters['pinOrder']=='BYNAME':
                pin_pair_str = check_pin_list_sorted(i+1)
            elif dict_parameters['pinOrder'] == 'PQFP':
                pin_pair_str = checkPinList(str(i+1)) + ' ' + str(i+1)
     
            elif dict_parameters['pinOrder'] == 'PLCC':
                print('PLCC not implemented yet sorry')
                exit(0)
            else:
                print('order not compatible with number of sides provided')
                exit(0)
                
            outstring += 'X '+ pin_pair_str + ' ' + str(posx) + ' ' + str(posy) + ' '\
                        + str(length) + ' ' + side + ' ' + str(text_size) + ' ' + \
                        str(text_size) + ' 1 1 ' + type_pin + '\n'
    else:
        print('wrong nbSide')
else:
    print('unknown package type')
    sys.exit(0)

dest_lib = ''
if dict_parameters['outLibrary']!='' and dict_parameters['outLibrary'].endswith('.lib'):
    if os.path.isfile(dict_parameters['outLibrary']):
        print('part will be added to ' +dict_parameters['outLibrary'] + ' library')
        dest_lib = dict_parameters['outLibrary']
        fileout = dict_parameters['outLibrary'][:-4]+ 'temp'
    else:
        print('creating a new library: ' + dict_parameters['outLibrary'])
        fileout = dict_parameters['outLibrary'][:-4]
else:
    fileout = dict_parameters['name']
    print('creating a new library: ' + fileout)
print(fileout)
docstring = 'EESchema-DOCLIB Version 2.0\n#\n$CMP '+dict_parameters['name']+'\n'
docstring += 'D ' + dict_parameters['Description'] + '\n'
docstring += 'K ' + dict_parameters['keywords'] + '\n'
docstring += 'F ' + dict_parameters['datasheet'] + '\n'
docstring += '$ENDCMP\n#\n#End Doc Library'

with open(fileout+'.dcm','w+') as docfile:
   docfile.write(docstring) 

with open(fileout+'.lib', 'w+') as outfile:
    outstring += 'ENDDRAW\nENDDEF\n#\n#End Library'
    outfile.write(outstring)

if dest_lib !='':
#    os.system('python '+os.path.join(os.getcwd(),'move_part.py') + ' ' + dict_parameters['name'] + ' ' + fileout+'.lib' + ' ' + dest_lib )
    os.system('move_part.py' + ' ' + dict_parameters['name'] + ' ' + fileout+'.lib' + ' ' + dest_lib )
    os.remove(fileout+'.lib')
    os.remove(fileout+'.dcm')
