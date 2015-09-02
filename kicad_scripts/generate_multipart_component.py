#!/usr/bin/env python

from __future__ import print_function
import os
import argparse
import time
import sys
import csv
from collections import OrderedDict
import operator

if len(sys.argv) >1:
    infile = sys.argv[1]
else:
    print('please provide a configuration file')
    sys.exit()


################################
##### Function declaration #####
################################
#function to override for each manufacturer
def importCSV(filename):
# expected csv format: 
# PIN_NAME, Function, Alternative func, Bank, PIN_NUMBER
  if not os.path.isfile(filename):
    print('pinfile not found')
    return
  with open(filename, mode='r') as infile2:
    first = True;
    reader2 = csv.reader(infile2)
    banks={}
    for row in reader2:
      if first:
#        print(row)
        for i in range(len(row)):
          if row[i] == 'Bank':
            bankIdx = i
            break
        first = False
        continue
      banks[row[bankIdx]]={}
#    print(banks)
#    print(len(banks))
  with open(filename, mode='r') as infile:
    first = True;
    reader = csv.reader(infile)
    for row in reader:
      if first:
#        print(row)
        first = False
        continue
#      print(row)
#      print(banks[row[bankIdx]])
      string = row[0]
      if row[2] != '-':
        string+= '/'+row[2]
      if row[3] != '-':
        string+= '/'+row[3]
      if row[1] != '-':
        string+= '/BANK'+row[1]
      banks[row[bankIdx]][row[4]]=string#(row[0]+'/'+row[1]+'/'+row[2])
#        pinlist[int(row[3])][row[5]]=str(row[0]+'/'+row[1]+'/'+row[2])
#  print(pinlist[0])
#  print(len(banks['0']))
#  print(banks['0'])
  return banks

def correctModuloTable(table):
    for r in table:
        if r%100 != 0:
            r -= r%100
    return table

def correctModulo(val):
  if val%100 != 0:
    val -= val%100
  return val
def rectCorners(NbPin, nbside, step):#, stepy, initoffsetx, initoffsety):
# return coordinate of top-left and bottom-right corner of the schematic rectangle
    res = []
    if nbside==1:
        res = [-step,-(step + NbPin/2*step), step, step + NbPin/2*step]
        res = correctModuloTable(res)
    elif nbside == 2:
            res = [-2*step,-NbPin/4*step-step,2*step,NbPin/4*step+step]
            res = correctModuloTable(res)
    elif nbside == 4:
        res = [-(2*step+NbPin/8*step), -(2*step+NbPin/8*step),\
                2*step+NbPin/8*step, 2*step+NbPin/8*step]
        res = correctModuloTable(res)
    return res
        
###############################################
##### Variable declaration/initialization #####
###############################################
if not os.path.isfile(infile) or infile == '':
  print('ERROR: config file doesnt exist')
  sys.exit()
dictParameters=OrderedDict([
('nbSide','1'),
('PinoutFile',''),
('outLibrary',''),
('name',''),
('alias',''),
('prefix','U'),
('datasheet',''),
('keywords',''),
('footprintFormat',''),
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
# fill dictparam with value from cofig file
with open(infile,'r+') as inf:
    while True:
        line = inf.readline()
        line = line.replace('\n','')
        if not line: break
        lsplit=[]
        lsplit.append(line[0:line.find('=')])
        lsplit.append(line[line.find('=')+1:])
#        lsplit = line.split('=')
        if lsplit[0] in dictParameters:
          if (lsplit[1] != '' and lsplit[1]!= dictParameters[lsplit[0]]):
            dictParameters[lsplit[0]]=lsplit[1]
if dictParameters['PinoutFile'] == '':
  print('you need to provide a PinoutFile')
  sys.exit()
banks = importCSV(dictParameters['PinoutFile'])
if banks == {}:
  print('parsing failed verify the format of your CSV file')
  sys.exit()
#name = 'testBanks'
length = 200
typePin = 'U'
textSize = 50
step = 100
stdString = '" 0 0 50 H I C C'
outstring = 'EESchema-LIBRARY Version 2.2 Date: ' + time.strftime("%d/%m/%Y") + '-' + time.strftime('%H:%M:%S') + '\n'
outstring += '#encoding utf-8\n#\n# ' + dictParameters['name'] + '\n#\nDEF '
#create a component with all the fields
outstring += dictParameters['name'] + ' U 0 40 Y Y '+ str(len(banks)) + ' F N\n'
outstring += 'F0 "' + dictParameters['prefix'] + '" 0 '+ str(len(banks['-']) *step+ 2*textSize) + ' 50 H V C C\n'
outstring += 'F1 "' + dictParameters['name'] + '" 0 ' + str(0 - 2*textSize) + ' 50 H V C C\n'
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
        outstring += 'F'+str(i-4)+' "' + dictParameters[key] + stdString + ' "' + key + '"\n'
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
unit = 1
for key in banks:
  #create a rectangle for each bank
  Npin = len(banks[key])
  halfNpin = Npin /2
  [rectxmin,rectymin,rectxmax,rectymax] = rectCorners(Npin,2,step)
  # modified rectx min and max according to lenght of pinname
  lenmax=0
  for keypin,value in sorted(banks[key].items(), key=operator.itemgetter(1)):
    if len(value) > lenmax:
      lenmax = len(value)
#  print(lenmax)
  rectxmax = max(300,int(lenmax * textSize / float(length) * 2*step))
  rectxmin = -rectxmax
  rectxmax = correctModulo(rectxmax)
  rectxmin = correctModulo(rectxmin)
#  print(rectxmax)
  outstring += 'S '+str(rectxmin)+' '+str(rectymin)+' '+str(rectxmax)+' ' +\
              str(rectymax) + ' ' + str(unit) + ' 1 0 f\n'
  #add the pins
  index=0
  sortedlist = sorted(banks[key].items(), key=operator.itemgetter(1))
#  print()
#  print(sortedlist)
  for keypin,value in sorted(banks[key].items(), key=operator.itemgetter(1)):
    if index <= Npin/2:
      posx = rectxmin - length
      posy = rectymin + step + (halfNpin-index) * step
      side = 'R'
    else:
      posx = rectxmax + length
      posy = rectymin + step + (Npin-index) * step
      side = 'L'
    outstring += 'X '+ value + ' ' + keypin + ' ' + str(posx) + ' ' +\
                str(posy) + ' ' + str(length)\
                + ' ' + side + ' ' + str(textSize) + ' ' + \
                str(textSize) + ' '+ str(unit) + ' 1 ' + typePin + '\n'
    index += 1
  unit+=1
#print(outstring)

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
