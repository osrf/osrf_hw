#!/usr/bin/env python

import os
import argparse
import time
import sys
import csv

#FIXME Add fields F4-F21 (add only necessary according to Reference ?)
#TODO allow config file instead of commandline arguments
#TODO FEATURE: sort dictionary ? add pin by name and not by pin number ==> allow to put together power, banks etc
#               Would require a "TRUST MY PINOUT" file argument: +> sort + resize + give number of pins and CSV layout
#TODO Detect pinout file ? like check for known colums names: or ask user to put specific names to the column wanted
#LIMITATIONS doesnt handle UFBGA like packages
#TODO Implement PLCC (not necessary, needed only for footprint generation)
#FIXME Think if PQFP and PLCC are supposed to be square chips
#add list of packages ? or just number of pins ? 
stringhelp = '### SCH NUMEROTATION TYPES ###                                       \n'\
'#   ######## ONE SIDE ########                                             \n'\
'#                                                                          \n'\
'#      SIL          SIL-ALT                                                \n'\
'#       ___           ___                                                  \n'\
'#   1 --|  |       1--|  |                                                 \n'\
'#   2 --|  |   N/2+1--|  |                                                 \n'\
'#   3 --|  |       2--|  |                                                 \n'\
'#   . --|  |   N/2+2--|  |                                                 \n'\
'#   . --|  |     ...--|  |                                                 \n'\
'#   . --|  |     N/2--|  |                                                 \n'\
'#   N --|__|       N--|__|                                                 \n'\
'#                                                                          \n'\
'#                                                                          \n'\
'   ######## TWO SIDES ########                                             \n'\
'#                                                                          \n'\
'#        DIL                   CONN1             CONN2                     \n'\
'#       _____                  _____             _____                     \n'\
'#   1 --|    |--N          1 --|    |--2     1 --|    |--N/2+1             \n'\
'#   2 --|    |--           3 --|    |--4     2 --|    |--N/2+2             \n'\
'#   3 --|    |--^          . --|    |--      3 --|    |--                  \n'\
'#   . --|    |--.          . --|    |--.     . --|    |--.                 \n'\
'#   . --|    |--.          . --|    |--.     . --|    |--.                 \n'\
'#   . --|    |--N/2+2      . --|    |--.     . --|    |--.                 \n'\
'#  N/2--|____|--N/2+1     N-1--|____|--N    N/2--|____|--N                 \n'\
'#                                                                          \n'\
'#                                                                          \n'\
'#  ######### FOUR SIDES #########                                          \n'\
'#                                                                          \n'\
'#              PLCC                                PQFP                    \n'\
'#              <--     <--                       <--     <--               \n'\
'#       __|_|_|_|_|_|_|_|_                __|_|_|_|_|_|_|_|_               \n'\
'#     --|                 |--          1--|o                |--            \n'\
'#     --|                 |--          2--|                 |--            \n'\
'#     --|                 |-- ^        3--|                 |-- ^          \n'\
'#     --|                 |-- |         --|                 |-- |          \n'\
'#    1--|o                |--           --|                 |--            \n'\
'#    2--|                 |--           --|                 |--            \n'\
'#    3--|                 |--           --|                 |--            \n'\
'#     --|                 |-- ^         --|                 |-- ^          \n'\
'#     --|_________________|-- |         --|_________________|-- |          \n'\
'#         | | | | | | | |                   | | | | | | | |                \n'\
'#           -->      -->                      -->      -->                 \n'\
'#                                                                          \n'\
'#  ############ BGA #############                                          \n'\
'#       1 2 3 4 ....                                                       \n'\
'#      ___________________________                                         \n'\
'#    A|o o o o o o o o o o o o o o| ^                                      \n'\
'#    B|o o o o o o o o o o o o o o| |                                      \n'\
'#    C|o o o o o o o o o o o o o o| |                                      \n'\
'#    .|o o o o o o o o o o o o o o| |                                      \n'\
'#    .|o o o o o <------>o o o o o| |                                      \n'\
'#    .|o o o o o ^ NIntw o o o o o| |           ==> BGA Represented as PGFP\n'\
'#     |o o o o o |       o o o o o| |  height                              \n'\
'#     |o o o o o |NInth  o o o o o| |                                      \n'\
'#     |o o o o o |       o o o o o| |                                      \n'\
'#     |o o o o o ^       o o o o o| |                                      \n'\
'#     |o o o o o o o o o o o o o o| |                                      \n'\
'#     |o o o o o o o o o o o o o o| |                                      \n'\
'#     |o o o o o o o o o o o o o o| |                                      \n'\
'#     |___________________________| |                                      \n'\
'#               width               ^                                      \n'\
'#     <---------------------------->                                       \n'

print(stringhelp)
parser = argparse.ArgumentParser()
parser.add_argument('-p','--package', default='DIL', help='[SIL,SIL-ALT,DIL,CONN1,CONN2,PLCC,PQFP]')
parser.add_argument('-t','--typechip', default='OTHER', help='type of chip (BGA or OTHER)')
parser.add_argument('--height', default=0,type=int,help='number of vertical balls')
parser.add_argument('--width', default=0,type=int, help='number of horizontal balls UNUSED IF CONNx')
parser.add_argument('--NInth',default=0,type=int, help='number of missing rows in the center of the package ONLY IF BGA')
parser.add_argument('--NIntw',default=0,type=int, help='number of missing cols in the center of the package ONLY IF BGA')
parser.add_argument('--name',default='COMPONENT_NAME', help='component name')
parser.add_argument('--prefix',default='U', help='component prefix')
parser.add_argument('--footprint',default='NO_FOOTPRINT', help='footrpint reference LIBRARYNAME:FOOTPRINTNAME')
parser.add_argument('--brief',default='DESCRIPTION', help='component/package description')
parser.add_argument('-f', '--pinoutFile',default='', help='path of the pinout CSV file: CSV format should be: PIN_NAME,PIN_NUMBER')
parser.add_argument('-d', '--datasheet',default='http://www.digikey.com', help='URI of the datasheet')
parser.add_argument('-k', '--keywords',default='Some Keywords', help='Keyword defining the component for quick search')

args = parser.parse_args()

################################
##### Function declaration #####
################################

def importCSV(filename):
# expected csv format: 
# PIN_NAME,PIN_NUMBER
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        pinDict = {rows[1]:rows[0] for rows in reader}
    return pinDict
def correctModulo(table):
    for r in table:
        if r%100 != 0:
            r -= r%100
    return table

def rectCorners(width,height, typechip, package, stepx, stepy, initoffsetx, initoffsety):
# return coordinate of top-left and bottom-right corner of the schematic rectangle
    res = []
    if typechip == 'BGA':
        res = [-(2*initoffsetx+(width*height-args.NIntw*args.NInth)/8*stepx),\
                -(2*initoffsety+(width*height-args.NIntw*args.NInth)/8*stepy),\
                2*initoffsetx+(width*height-args.NIntw*args.NInth)/8*stepx, \
                2*initoffsety+(width*height-args.NIntw*args.NInth)/8*stepy]
        res = correctModulo(res)
        return res
    elif typechip == 'OTHER':
        if package == 'SIL' or package == 'SIL-ALT':
            res = [-initoffsetx,-(initoffsety + height/2*stepy), initoffsetx, initoffsety + height/2*stepy]
            res = correctModulo(res)
            return res
        elif package == 'DIL' or package == 'CONN1' or package == 'CONN2':
            if(width !=2):
                print('WARNING: assume width=2 because of package chosen')
                res = [-2*initoffsetx,-height/2*stepy-initoffsety,2*initoffsetx,height/2*stepy+initoffsety]
                res = correctModulo(res)
                return res
        elif package == 'PLCC' or package == 'PQFP':
            Npin = 2*height+2*width
            res = [-(2*initoffsetx + Npin/8*stepx),-(2*initoffsety + Npin/8*stepy)\
                    , 2*initoffsetx + Npin/8*stepx, 2*initoffsety + Npin/8*stepy]
            res = correctModulo(res)
            return res
        else:
            print('unknown package, expected SIL,SIL-ALT,DIL,CONN1,CONN2,PLCC,PQFP')
    else:
        print 'unknown type of chip, expected BGA or OTHER'
    sys.exit(0)
        
# WARNING here pinnumber is a string
#checks if the pin exist in the dictionary, if not the pin will be named:\
# PIN_"PIN_NUMBER" for example A5 will be named PIN_A5
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
#Not existing letters in BGA naming: I,O,Q,S,X,Z,
BGAdico=['A','B','C','D','E','F','G','H','J','K','L','M','N','P','R','T','U','V',\
        'W','Y','AA','AB','AC','AD','AE','AF','AG','AH','AJ','AK']
length = 300
typePin = 'U'
textSize = 50
stepx = 200; stepy = 200
initoffsetx = 200
initoffsety = 200
#TODO Add other parameters F4 -> F21
[rectxmin,rectymin,rectxmax,rectymax]=rectCorners(args.width,args.height,args.typechip,args.package,stepx,stepy,initoffsetx,initoffsety)
outstring = 'EESchema-LIBRARY Version 2.2 Date: ' + time.strftime("%d/%m/%Y") + '-' + time.strftime('%H:%M:%S') + '\n'
outstring += '#encoding utf-8\n#\n# ' + str(args.name) + '\n#\nDEF '
outstring += args.name + ' U 0 40 Y Y 1 F N\n'
outstring += 'F0 "' + args.prefix + '" ' + str(rectxmin) + ' ' + str(rectymax+2*textSize) + ' 50 H V C C\n'
outstring += 'F1 "' + args.name + '" ' + str(rectxmin) + ' ' + str(rectymin - 2*textSize) + ' 50 H V C C\n'
outstring += 'F2 "' + args.footprint + '" 0 ' + str(-textSize)+ ' 50 H I C C\n'
outstring += 'F3 "' + args.brief + '" 0 ' + str(textSize) + ' 50 H I C C\nDRAW\n'
outstring += 'S '+str(rectxmin)+' '+str(rectymin)+' '+str(rectxmax)+' '\
             +str(rectymax)+ ' 0 1 0 f\n'

# import pins from provided CSV file
if args.pinoutFile != '' and os.path.isfile(args.pinoutFile):
    pinDico = importCSV(args.pinoutFile) 
    usePinList = 1
else:
    usePinList = 0

# Check if chip is a BallArray or a regular chip
if args.typechip == 'BGA':
    if args.width>30 or args.height>30:
        print('BGA dimension cannot exceed 30 balls per side (900 pins)')
        sys.exit(0)
    Npin = args.height*args.width - args.NIntw*args.NIntw
    quarterNpin = Npin/4
    halfNpin = Npin/2
    threeQuartNpin = 3*quarterNpin
    index = 0; iforbidmin=0;iforbidmax=0;jforbidmin=0;jforbidmax=0;
    if(args.NIntw != 0 and args.NInth != 0):
        iforbidmin = (args.height-args.NInth)/2
        iforbidmax = args.height - iforbidmin + args.NInth/2
        jforbidmin = (args.width-args.NIntw)/2
        jforbidmax = args.width - jforbidmin + args.NIntw/2
    for i in range(args.height):
        for j in range(args.width):
            # skip center balls if needed
            if(not(i > iforbidmin and i< iforbidmax and j>jforbidmin and j<jforbidmax)):
                index += 1
                string = BGAdico[i]+str(j+1)
                if index <= quarterNpin:
                    side = 'R'
                    posx = rectxmin - length
                    posy = rectymin + 2*initoffsety + (quarterNpin-index+1)*stepy
                elif index <= halfNpin:
                    side = 'U'
                    posx = rectxmin + 2*initoffsetx + ((index-quarterNpin))*stepx
                    posy = rectymin - length
                elif index <= threeQuartNpin:
                    side = 'L'
                    posx = rectxmax + length
                    posy = rectymin + 2*initoffsety + (index-halfNpin)*stepy
                else:
                    side = 'D'
                    posx = rectxmin + 2*initoffsetx + (Npin-(index))*stepx
                    posy = rectymax + length
                outstring += 'X '+ checkPinList(string) + ' ' + string\
                            + ' ' + str(posx) + ' ' + str(posy) + ' ' + str(length)\
                            + ' ' + side + ' ' + str(textSize) + ' ' + \
                            str(textSize) + ' 1 1 ' + typePin + '\n'
elif args.typechip == 'OTHER':
    #### One side schematics ###
    side = 'R'
    if args.package == 'SIL':
        for i in range(args.height):
            outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                        + ' ' + str(rectxmin - length) + ' ' + str(rectymin + \
                        initoffsety + (args.height-i)*stepy) + ' ' + str(length)\
                        + ' ' + side + ' ' + str(textSize) + ' ' + \
                        str(textSize) + ' 1 1 ' + typePin + '\n'
    elif args.package == 'SIL-ALT':
        for i in range(args.height):
            if i%2==0:
                outstring += 'X '+ checkPinList(str(i/2+1)) + ' ' + str(i/2+1)\
                             + ' ' + str(rectxmin - length) + ' ' + str(rectymin + \
                            initoffsety + (args.height-i)*stepy) + ' ' + \
                            str(length) + ' ' + side + ' ' + str(textSize)\
                            + ' ' + str(textSize) + ' 1 1 ' + typePin + '\n'
            else:
                outstring += 'X '+ checkPinList(str((args.height+i)/2+1)) + ' '\
                            + str((args.height+i)/2+1) + ' ' + str(rectxmin - \
                            length) + ' ' + str(rectymin + initoffsety + \
                            (args.height-i)*stepy) + ' ' + str(length) + ' ' +\
                            side + ' ' + str(textSize) + ' ' + \
                            str(textSize) + ' 1 1 ' + typePin + '\n'
                
    ### Two sides schematics ###
    elif args.package == 'CONN2':
        for i in range(2*args.height):
            if i < args.height:
                posx = rectxmin - length
                posy = rectymin + initoffsety + (args.height-i) * stepy
                side = 'R'
            else:
                posx = rectxmax + length
                posy = rectymin + initoffsety + (2*args.height-i) * stepy
                side = 'L'
            outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                        + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                        str(length) + ' ' + side + ' ' + str(textSize)\
                        + ' ' + str(textSize) + ' 1 1 ' + typePin\
                        + '\n'

    elif args.package == 'CONN1':
        for i in range(2*args.height):
            if i%2 ==0:
                posx = rectxmin - length
                posy = rectymin + initoffsety + (args.height-i/2) * stepy
                side = 'R'
            else:
                posx = rectxmax + length
                posy = rectymin + initoffsety + (args.height-i/2) * stepy
                side = 'L'
            outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                        + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                        str(length) + ' ' + side + ' ' + str(textSize)\
                        + ' ' + str(textSize) + ' 1 1 ' + typePin\
                        + '\n'

    elif args.package == 'DIL':
        for i in range(2*args.height):
            if i < args.height:
                posx = rectxmin - length
                posy = rectymin + initoffsety + (args.height-i) * stepy
                side = 'R'
            else:
                posx = rectxmax + length
                posy = rectymin + initoffsety + (i-args.height+1) * stepy
                side = 'L'
            outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                        + ' ' + str(posx) + ' ' + str(posy) + ' ' +\
                        str(length) + ' ' + side + ' ' + str(textSize)\
                        + ' ' + str(textSize) + ' 1 1 ' + typePin\
                        + '\n'
            
    ### Four sides schematics ###
    elif args.package == 'PQFP':
        Npin = 2*args.height+2*args.width
        quarterNpin = Npin/4
        halfNpin = Npin/2
        threeQuartNpin = 3*quarterNpin
        for i in range(Npin):
            if i < quarterNpin:
                side = 'R'
                posx = rectxmin - length
                posy = rectymin + initoffsety + (quarterNpin-i)*stepy
            elif i < halfNpin:
                side = 'U'
                posx = rectxmin + initoffsetx + ((i+1-quarterNpin))*stepx
                posy = rectymin - length
            elif i< threeQuartNpin:
                side = 'L'
                posx = rectxmax + length
                posy = rectymin + initoffsety + (i+1-halfNpin)*stepy
            else:
                side = 'D'
                posx = rectxmin + initoffsetx + (Npin-(i-1))*stepx
                posy = rectymax + length
    
            outstring += 'X '+ checkPinList(str(i+1)) + ' ' + str(i+1)\
                        + ' ' + str(posx) + ' ' + str(posy) + ' ' + str(length)\
                        + ' ' + side + ' ' + str(textSize) + ' ' + \
                        str(textSize) + ' 1 1 ' + typePin + '\n'
    elif args.package == 'PLCC':
        print('PLCC not implemented yet sorry')
        exit(0)
else:
    print 'unknown package type'
    sys.exit(0)
# after pin definition add
with open(args.name+'.lib', 'w+') as outfile:
    outstring += 'ENDDRAW\nENDDEF\n#\n#End Library'
    outfile.write(outstring)

docstring = 'EESchema-DOCLIB Version 2.0\n#\n$CMP '+args.name+'\n'
docstring += 'D ' + args.brief + '\n'
docstring += 'K ' + args.keywords + '\n'
docstring += 'F ' + args.datasheet + '\n'
docstring += '$ENDCMP\n#\n#End Doc Library'

with open(args.name+'.dcm','w+') as docfile:
   docfile.write(docstring) 

