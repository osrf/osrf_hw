#!/usr/bin/env python

# This scripts take a config file just as generate_component.py.
# Advantage: create a different component unit/section/rectangle for every different bank of your device
# Restriction: - must provide a csv file with the complete pinout of your chip, every size parameter will be ignored
#              - the csv file must contain a column containing "Bank" to allow multi part generation according to Bank number
#              - the pin number (e.g A11 or 42) are located in the last column
#              - the csv file must contain only a title row
#              - only 1 component / package per csv file

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
#TODO adapt it for uControllers
#FIXME assumes that last column is the pin number
#FIXME assumes that the component has several banks and that one column contains "Bank" string
def import_csv(filename): 
# expected csv format: 
# ....,BANK,..., PIN_NUMBER
  if not os.path.isfile(filename):
    print('pinfile not found')
    return
  with open(filename, mode='r') as infile2:
    first = True;
    reader2 = csv.reader(infile2)
    banks={}
    for row in reader2:
      if first:
        for i in range(len(row)):
          if row[i].find('Bank') != -1:
            bank_idx = i
            break
        first = False
        continue
      banks[row[bank_idx]]={}
  with open(filename, mode='r') as infile:
    first = True;
    reader = csv.reader(infile)
    for row in reader:
      if first:
        first = False
        continue
      string = ''
      for i in range(len(row)-1):
        if i == bank_idx:
          continue
        if row[i] != '-' and row[i] != '':
          if string != '':
            string += '/'
          string+= row[i]
      if row[bank_idx] != '-' and row[bank_idx] != '':
        string+= '/BANK'+row[bank_idx]
      banks[row[bank_idx]][row[-1]]=string
  return banks

def correct_modulo_table(table):
    for r in table:
        if r%100 != 0:
            r -= r%100
    return table

def correct_modulo(val):
  if val%100 != 0:
    val -= val%100
  return val
def rect_corners(nb_pin, nbside, step):#, stepy, initoffsetx, initoffsety):
# return coordinate of top-left and bottom-right corner of the schematic rectangle
    res = []
    if nbside==1:
        res = [-step,-(step + nb_pin/2*step), step, step + nb_pin/2*step]
        res = correct_modulo_table(res)
    elif nbside == 2:
            res = [-2*step,-nb_pin/4*step-step,2*step,nb_pin/4*step+step]
            res = correct_modulo_table(res)
    elif nbside == 4:
        res = [-(2*step+nb_pin/8*step), -(2*step+nb_pin/8*step),\
                2*step+nb_pin/8*step, 2*step+nb_pin/8*step]
        res = correct_modulo_table(res)
    return res
        
###############################################
##### Variable declaration/initialization #####
###############################################
if not os.path.isfile(infile) or infile == '':
  print('ERROR: config file doesnt exist')
  sys.exit()
dict_param=OrderedDict([
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
        if lsplit[0] in dict_param:
          if (lsplit[1] != '' and lsplit[1]!= dict_param[lsplit[0]]):
            dict_param[lsplit[0]]=lsplit[1]
if dict_param['PinoutFile'] == '':
  print('you need to provide a PinoutFile')
  sys.exit()
banks = import_csv(dict_param['PinoutFile'])
if banks == {}:
  print('parsing failed verify the format of your CSV file')
  sys.exit()
print(banks)
#name = 'testBanks'
length = 200
type_pin = 'U'
text_size = 50
step = 100
std_string = '" 0 0 50 H I C C'
outstring = 'EESchema-LIBRARY Version 2.3\n'
outstring += '#encoding utf-8\n#\n# ' + dict_param['name'] + '\n#\nDEF '
#create a component with all the fields
outstring += dict_param['name'] + ' U 0 40 Y Y '+ str(len(banks)) + ' F N\n'
#  outstring += 'F0 "' + dict_param['prefix'] + '" 0 '+ str(len(banks[key]) *step+ 2*text_size) + ' 50 H V C C\n'
outstring += 'F0 "' + dict_param['prefix'] + '" 0 0 50 H V C C\n'
outstring += 'F1 "' + dict_param['name'] + '" 0 ' + str(0 - 2*text_size) + ' 50 H V C C\n'
outstring += 'F2 "_'+ std_string +'\n'
outstring += 'F3 "' + dict_param['datasheet'] + std_string + '\n'
outstring += 'F4 "' + dict_param['MFN'] + std_string + ' "MFN"\n'
outstring += 'F5 "' + dict_param['MFP'] + std_string + ' "MFP"\n'
outstring += 'F6 "digikey' + std_string + ' "D1"\n'
outstring += 'F7 "mouser' + std_string + ' "D2"\n'
i=0
for key in dict_param:
#17 = index of D1PN
    if(i>len(dict_param)-16):
        outstring += 'F'+str(i-4)+' "' + dict_param[key] + std_string + ' "' + key + '"\n'
    i+=1

# Add Alias
if dict_param['alias'] != '':
    outstring += 'ALIAS ' + dict_param['alias'] + '\n'
# Add footprint list
if dict_param['footprintFormat'] != '':
    outstring += '$FPLIST\n'
    for elt in dict_param['footprintFormat'].split(','):
        if elt !='':
            outstring += ' ' + elt + '\n'
    outstring += '$ENDFPLIST\n'

outstring += 'DRAW\n'
unit = 1
for key,val in sorted(banks.items()):
  #create a rectangle for each bank
  npin = len(banks[key])
  halfnpin = npin /2
  [rectxmin,rectymin,rectxmax,rectymax] = rect_corners(npin,2,step)
  # modified rectx min and max according to lenght of pinname
  lenmax=0
  for keypin,value in sorted(banks[key].items(), key=operator.itemgetter(1)):
    if len(value) > lenmax:
      lenmax = len(value)
#  print(lenmax)
  rectxmax = max(300,int(lenmax * text_size / float(length) * 2*step))
  rectxmin = -rectxmax
  rectxmax = correct_modulo(rectxmax)
  rectxmin = correct_modulo(rectxmin)
#  print(rectxmax)
  outstring += 'S '+str(rectxmin)+' '+str(rectymin)+' '+str(rectxmax)+' ' +\
              str(rectymax) + ' ' + str(unit) + ' 1 0 f\n'
  #add the pins
  index=0
  sortedlist = sorted(banks[key].items(), key=operator.itemgetter(1))
#  print()
#  print(sortedlist)
  for keypin,value in sorted(banks[key].items(), key=operator.itemgetter(1)):
    if index <= npin/2:
      posx = rectxmin - length
      posy = rectymin + step + (halfnpin-index) * step
      side = 'R'
    else:
      posx = rectxmax + length
      posy = rectymin + step + (npin-index) * step
      side = 'L'
    outstring += 'X '+ value + ' ' + keypin + ' ' + str(posx) + ' ' +\
                str(posy) + ' ' + str(length)\
                + ' ' + side + ' ' + str(text_size) + ' ' + \
                str(text_size) + ' '+ str(unit) + ' 1 ' + type_pin + '\n'
    index += 1
  unit+=1
#print(outstring)

dest_lib = ''
if dict_param['outLibrary']!='' and dict_param['outLibrary'].endswith('.lib'):
    if os.path.isfile(dict_param['outLibrary']):
        print('part will be added to ' +dict_param['outLibrary'] + ' library')
        dest_lib = dict_param['outLibrary']
        fileout = dict_param['outLibrary'][:-4]+ 'temp'
    else:
        print('creating a new library: ' + dict_param['outLibrary'])
        fileout = dict_param['outLibrary'][:-4]
else:
    fileout = dict_param['name']
    print('creating a new library: ' + fileout)
print(fileout)
docstring = 'EESchema-DOCLIB  Version 2.0\n#\n$CMP '+dict_param['name']+'\n'
docstring += 'D ' + dict_param['Description'] + '\n'
docstring += 'K ' + dict_param['keywords'] + '\n'
docstring += 'F ' + dict_param['datasheet'] + '\n'
docstring += '$ENDCMP\n#\n#End Doc Library'

with open(fileout+'.dcm','w+') as docfile:
   docfile.write(docstring) 

with open(fileout+'.lib', 'w+') as outfile:
    outstring += 'ENDDRAW\nENDDEF\n#\n#End Library'
    outfile.write(outstring)

if dest_lib !='':
#    os.system('python '+os.path.join(os.getcwd(),'move_part.py') + ' ' + dict_param['name'] + ' ' + fileout+'.lib' + ' ' + dest_lib )
    os.system('move_part.py' + ' ' + dict_param['name'] + ' ' + fileout+'.lib' + ' ' + dest_lib )
    os.remove(fileout+'.lib')
    os.remove(fileout+'.dcm')
