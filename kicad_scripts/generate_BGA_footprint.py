#!/usr/bin/env python

from __future__ import print_function
import os
import sys
from collections import OrderedDict
#FIXME Best way to configur pad size? right now we use half the pitch

if len(sys.argv) >1:
    infile = sys.argv[1]
else:
    print('please provide a configuration file')
    sys.exit()

dictParameters=OrderedDict([
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
        if lsplit[0] in dictParameters:
          if (lsplit[1] != '' and lsplit[1]!= dictParameters[lsplit[0]]):
            dictParameters[lsplit[0]]=lsplit[1]

#retrieve BGA package parameters
string = dictParameters['name']
idx = string.find('P')
pitch = float(string[string.find('C')+1:idx])/100.0
str2 = string[idx + 1 :] 
idx = str2.find('X')
nBallx = int(str2[:idx])
str2 = str2[idx+1:]
idx = str2.find('_')
nBally = int(str2[:idx])
str2 = str2[idx+1:]
idx = str2.find('X')
lenx = float(str2[:idx])/100.0
str2 = str2[idx+1:]
idx = str2.find('X')
leny = float(str2[:idx])/100.0

def drawRect(x,y,layer):
    print(layer)
    print(x)
    print(y)
    width = 0.15
    if layer.find('CrtYd') != -1:
        width = 0.05
    string = '  (fp_line (start -{} -{}) (end -{} {}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
    string += '  (fp_line (start -{} -{}) (end {} -{}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
    string += '  (fp_line (start {} {}) (end -{} {}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
    string += '  (fp_line (start {} {}) (end {} -{}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
    return string

def createPinList(nBallx,nBally):
    letterBGA= ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','R','T','U','V','W','Y']
    pinlist = []
    for i in range(nBallx):
        for j in range(nBally):
            firstletter = j/len(letterBGA)
            defstr = ''
            if(firstletter != 0):
                defstr = letterBGA[firstletter-1]
            pinlist.append(defstr+letterBGA[j-firstletter*len(letterBGA)]+str(i+1))
    return pinlist

outstring = "(module " + dictParameters['name'] + ' (layer F.Cu)\n'      # module name
outstring += '  (descr "'+dictParameters['Description'] + '")\n'        # Description
outstring += '  (tags "'+dictParameters['keywords'] + '")\n'            # keywords
outstring += '  (attr smd)\n'                                           # attribute
outstring += '  (fp_text reference REF** (at 0 {0}) (layer F.SilkS)\n'.format(int(leny/2.+2))  # reference
outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
outstring += '  )\n'
outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dictParameters['name'],int(leny/2.+2))  # value
outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
outstring += '  )\n'
outstring += drawRect(lenx/2.,leny/2.,'F.SilkS')            # silkscreen rectangle
outstring += drawRect(lenx/2.+0.2,leny/2.+0.2,'F.CrtYd')    # courtyard rectangle
outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+0.5,leny/2.+0.5,lenx/2.+1,leny/2.+0.5)#silkscreen circle

pinlist = createPinList(nBallx,nBally)
minx = (nBallx-1)*pitch/2.; miny = (nBally-1)*pitch/2.
pn = 0 ; posx = -minx ; posy = -miny ; bsize = pitch/2.
for pin in pinlist:
    if pn % nBallx == 0 and pn / nBallx != 0: # if we start a new column
        posx += pitch
        posy = -miny
    if abs(posx)<0.001: #avoid python precision issue
        posx = 0
    if abs(posy)<0.001: #avoid python precision issue
        posy = 0
    outstring += '  (pad {} smd circle (at {} {}) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(pin,posx,posy,bsize,bsize)
    posy += pitch
    pn += 1
outstring += '  (model '+str(os.path.join(dictParameters['3dModelPath'],dictParameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
outstring += ')'
outfilepath = os.path.join(dictParameters['outLibrary'],dictParameters['name']+'.kicad_mod')
print(outfilepath)
with open(outfilepath,'w+') as outfile:
    outfile.write(outstring)
