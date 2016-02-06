#! /usr/bin/env python

from __future__ import print_function
import os
import re
import sys
from collections import OrderedDict
import generate_standard_footprints as genIC

#TODO Add support for BGA chip with different pitch in x and y dimension
#FIXME 3D models added with absolute path, not relative to KISYS3DMOD
if len(sys.argv) >1:
    infile = sys.argv[1]
else:
    print('please provide a configuration file')
    sys.exit()
dico_param=OrderedDict([
('outLibrary',''),
('name',''),
('keywords',''),
('Description','_'),
('3dModelPath','_') ])

with open(infile,'r+') as inf:
    while True:
        line = inf.readline()
        line = line.replace('\n','')
        if not line: break
        lsplit=[]
        lsplit.append(line[0:line.find('=')])
        lsplit.append(line[line.find('=')+1:])
        if lsplit[0] in dico_param:
          if (lsplit[1] != '' and lsplit[1]!= dico_param[lsplit[0]]):
            dico_param[lsplit[0]]=lsplit[1]

string = dico_param['name']
dig_index = re.search("\d",string)
pkgname = string[:dig_index.start()]
string = string[dig_index.start():]
array_BGA = ['C','P','X','_','X','X']
array_SON = ['P','X','X','-','N']
array_SOP = ['P','X','-','N']
array_SOIC = ['P','X','-','N']
array_QFN = ['P','X','X','-','_','X']
array_QFP = ['P','X','X','-','N']

def parsename(array,string):
  data = []
  for key in array:
    idx = string.find(key)
    data.append(float(string[:idx]))
    string = string[idx+1:]
  return [data,string]

if pkgname == 'BGA':
  [data,string] = parsename(genIC.array_BGA,string)
  data.append(float(string))
  print(data)
  if data[2]*data[3] != data[0]:
    print('{}*{} != {} ! please verify that your package name is valid'.format(data[2],data[3],data[0]))
    sys.exit(0)
  outstring = genIC.generate_BGA_footprint(dico_param,data)
  outfilepath = os.path.join(dico_param['outLibrary'],dico_param['name']+'.kicad_mod')
  print(outfilepath)
  with open(outfilepath,'w+') as outfile:
      outfile.write(outstring)
# pitch = paramArray[1]/100.0; nBallx = int(paramArray[2]); nBally = int(paramArray[3]); lenx = paramArray[4]/100.0; leny = paramArray[5]/100.0
  cmd = 'freecad freecad_gen_BGA.py ' + os.path.join(dico_param['3dModelPath'],dico_param['name']+'.wrl')
  cmd = 'freecad freecad_gen_BGA.py {} {} {} {} {} {} {} {}'.format(dico_param['3dModelPath'], dico_param['name'], data[1]/100.0, int(data[2]), int(data[3]), data[4]/100.0, data[5]/100.0, data[6]/100.0)
  print(cmd)
  os.system(cmd)

elif pkgname == 'QFN':
  [data,string] = parsename(genIC.array_QFN,string)
  data.append(float(string))
  print(data)
  outstring = genIC.generate_QFN_footprint(dico_param,data)
  outfilepath = os.path.join(dico_param['outLibrary'],dico_param['name']+'.kicad_mod')
  print(outfilepath)
  with open(outfilepath,'w+') as outfile:
      outfile.write(outstring)
elif pkgname == 'QFP':
  [data,string] = parsename(genIC.array_QFP,string)
  print(data) 
  outstring = genIC.generate_QFP_footprint(dico_param,data)
  outfilepath = os.path.join(dico_param['outLibrary'],dico_param['name']+'.kicad_mod')
  print(outfilepath)
  with open(outfilepath,'w+') as outfile:
      outfile.write(outstring)
elif pkgname == 'SON':
  [data,string] = parsename(genIC.array_SON,string)
  print(data) 
  #FIXME Thermal pad dimensions ??
elif pkgname == 'SOP' or pkgname == 'SOIC':
  [data,string] = parsename(genIC.array_SOP,string)
  print(data) 
  outstring = genIC.generate_SOP_footprint(dico_param,data)
  outfilepath = os.path.join(dico_param['outLibrary'],dico_param['name']+'.kicad_mod')
  print(outfilepath)
  with open(outfilepath,'w+') as outfile:
      outfile.write(outstring)
else:
  print('unknown package format')
  sys.exit(0)


