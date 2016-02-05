import os

arrayBGA = ['C','P','X','_','X','X']
arraySON = ['P','X','X','-','N']
arraySOP = ['P','X','-','N']
arraySOIC = ['P','X','-','N']
arrayQFN = ['P','X','X','-','_','X']
arrayQFP = ['P','X','X','-','N']

def drawRect(x,y,layer):
  width = 0.15
  if layer.find('CrtYd') != -1:
    width = 0.05
  string = '  (fp_line (start -{} -{}) (end -{} {}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  string += '  (fp_line (start -{} -{}) (end {} -{}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  string += '  (fp_line (start {} {}) (end -{} {}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  string += '  (fp_line (start {} {}) (end {} -{}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  return string

def generate_BGA_footprint(dictParameters,paramArray):
  pitch = paramArray[1]/100.0; nBallx = int(paramArray[2]); nBally = int(paramArray[3]); lenx = paramArray[4]/100.0; leny = paramArray[5]/100.0
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
  def create_pin_list(nBallx,nBally):
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
  
  pinlist = create_pin_list(nBallx,nBally)
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
  
  return outstring
      
def generate_QFN_footprint(dictParameters,paramArray):
  pitch = paramArray[0]/100.0; lenx = paramArray[1]/100.0; leny = paramArray[2]/100.0; npins = int(paramArray[4]); thPadx = paramArray[5]/100.0; thPady = paramArray[6]/100.0
  outstring = "(module " + dictParameters['name'] + ' (layer F.Cu)\n'      # module name
  outstring += '  (descr "'+dictParameters['Description'] + '")\n'        # Description
  outstring += '  (tags "'+dictParameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {}) (layer F.SilkS)\n'.format(int(leny/2.+4))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dictParameters['name'],int(leny/2.+4))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += drawRect(lenx/2.+0.1,leny/2.+0.1,'F.SilkS')            # silkscreen rectangle
  outstring += drawRect(lenx/2.+pitch+0.2,leny/2.+pitch+0.2,'F.CrtYd')    # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+1,leny/2.+1,lenx/2.+1,leny/2.+0.5)#silkscreen circle
  quartPin = npins/4; halfPin = npins/2; triquartPin = 3*quartPin
#  minx = (quartPin+2)*pitch/2.; miny = (quartPin+2)*pitch/2.
#FIXME pin #npin/8 shoud be y=0 #3*npin/8 should be x=0 etc
#this pad1x computation works only for square QFN
  test = npins/8.
  #if test % 2 == 0:
  pad1y = (test)*pitch - pitch/2
#  minx = (thPadx+0.2)/2. +3*pitch/4.; miny = (thPady+0.2)/2.+3*pitch/4.
  minx = lenx/2.; miny = leny/2.
  posx = -minx ; posy = -pad1y ; psizex = pitch*1.5; psizey = pitch/1.5 
  for pin in range(npins):
      if pin < quartPin:
          #posx = -minx
          if pin != 0:
            posy += pitch
      elif pin == quartPin:
          posx = -pad1y
          posy = miny
          psizex = pitch/1.5
          psizey = pitch*1.5
      elif pin < halfPin:
          #posy = miny
          posx += pitch
      elif pin == halfPin:
          posy = pad1y
          posx = minx
          psizex = pitch*1.5
          psizey = pitch/1.5
      elif pin < triquartPin:
          #posx = minx
          posy -= pitch
      elif pin == triquartPin:
          posx = pad1y
          posy = -miny
          psizex = pitch/1.5
          psizey = pitch*1.5
      else:
          #posy = -miny
          posx -= pitch
      if abs(posx)<0.001: #avoid python precision issue
          posx = 0
      if abs(posy)<0.001: #avoid python precision issue
          posy = 0
      outstring += '  (pad {} smd rect (at {} {}) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(pin+1,posx,posy,psizex,psizey)
  #add thermal pad
  outstring += '  (pad EPAD smd rect (at 0 0) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(thPadx+0.2,thPady+0.2)
  outstring += '  (model '+str(os.path.join(dictParameters['3dModelPath'],dictParameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring


def generate_QFP_footprint(dictParameters,paramArray):
#FIXME figure out if dimension is actual lead span or body dimension
  pitch = paramArray[0]/100.0; lenx = paramArray[1]/100.0; leny = paramArray[2]/100.0; npins = int(paramArray[4])
  nomsizex = 1.5
  nomsizey = pitch-0.1
  outstring = "(module " + dictParameters['name'] + ' (layer F.Cu)\n'      # module name
  outstring += '  (descr "'+dictParameters['Description'] + '")\n'        # Description
  outstring += '  (tags "'+dictParameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {}) (layer F.SilkS)\n'.format(int(leny/2.+4))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dictParameters['name'],int(leny/2.+4))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += drawRect(lenx/2.,leny/2.,'F.SilkS')            # silkscreen rectangle
  outstring += drawRect(lenx/2.+nomsizex,leny/2.+nomsizex,'F.CrtYd')            # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+1,leny/2.+1,lenx/2.+1,leny/2.+0.5)#silkscreen circle
  quartPin = npins/4; halfPin = npins/2; triquartPin = 3*quartPin
#  minx = (quartPin+2)*pitch/2.; miny = (quartPin+2)*pitch/2.
#FIXME pin #npin/8 shoud be y=0 #3*npin/8 should be x=0 etc
#this pad1x computation works only for square QFP
  test = npins/8.
  pad1y = (test)*pitch - pitch/2
  minx = (lenx+1.5)/2.; miny = (leny+1.5)/2.
  posx = -minx ; posy = -pad1y ; psizex = nomsizex; psizey = nomsizey
  for pin in range(npins):
      if pin < quartPin:
          if pin != 0:
            posy += pitch
      elif pin == quartPin:
          posx = -pad1y
          posy = miny
          psizex = nomsizey
          psizey = nomsizex
      elif pin < halfPin:
          posx += pitch
      elif pin == halfPin:
          posy = pad1y
          posx = minx
          psizex = nomsizex
          psizey = nomsizey
      elif pin < triquartPin:
          posy -= pitch
      elif pin == triquartPin:
          posx = pad1y
          posy = -miny
          psizex = nomsizey
          psizey = nomsizex
      else:
          posx -= pitch
      if abs(posx)<0.001: #avoid python precision issue
          posx = 0
      if abs(posy)<0.001: #avoid python precision issue
          posy = 0
      outstring += '  (pad {} smd rect (at {} {}) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(pin+1,posx,posy,psizex,psizey)
  outstring += '  (model '+str(os.path.join(dictParameters['3dModelPath'],dictParameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring

def generate_SOP_footprint(dictParameters,paramArray):
#FIXME Check nominal pad size for common SOP/SOIC packages
  pitch = paramArray[0]/100.0; lenx = paramArray[1]/100.0; leny = paramArray[2]/100.0; npins = int(paramArray[3]);
  nomsizex = 2
  nomsizey = pitch-0.1
  outstring = "(module " + dictParameters['name'] + ' (layer F.Cu)\n'     # module name
  outstring += '  (descr "'+dictParameters['Description'] + '")\n'        # Description
  outstring += '  (tags "'+dictParameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {}) (layer F.SilkS)\n'.format(int(leny/2.+4))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dictParameters['name'],int(leny/2.+4))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += drawRect(lenx/2.+0.1,leny/2.+0.1,'F.SilkS')            # silkscreen rectangle
  outstring += drawRect(lenx/2.+pitch+0.2,leny/2.+pitch+0.2,'F.CrtYd')    # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+1,leny/2.+1,lenx/2.+1,leny/2.+0.5)#silkscreen circle
  halfPin = npins/2
  test = npins/4.
  pad1y = (test)*pitch - pitch/2
  minx = (lenx+nomsizex)/2.; miny = (leny+nomsizex)/2.
  posx = -minx ; posy = -pad1y ; psizex = pitch*1.5; psizey = pitch/1.5 
  for pin in range(npins):
      if pin == 0:
        pass
      elif pin < halfPin:
          posy += pitch
      elif pin == halfPin:
          posy = pad1y
          posx = minx
          psizex = pitch*1.5
          psizey = pitch/1.5
      else:
          posy -= pitch
      if abs(posx)<0.001: #avoid python precision issue
          posx = 0
      if abs(posy)<0.001: #avoid python precision issue
          posy = 0
      outstring += '  (pad {} smd rect (at {} {}) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(pin+1,posx,posy,psizex,psizey)
  outstring += '  (model '+str(os.path.join(dictParameters['3dModelPath'],dictParameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring
