import os

array_BGA = ['C','P','X','_','X','X']
array_SON = ['P','X','X','-','N']
array_SOP = ['P','X','-','N']
array_SOIC = ['P','X','-','N']
array_QFN = ['P','X','X','-','_','X']
array_QFP = ['P','X','X','-','N']

def draw_rect(x,y,layer):
  width = 0.15
  if layer.find('CrtYd') != -1:
    width = 0.05
  string = '  (fp_line (start -{} -{}) (end -{} {}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  string += '  (fp_line (start -{} -{}) (end {} -{}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  string += '  (fp_line (start {} {}) (end -{} {}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  string += '  (fp_line (start {} {}) (end {} -{}) (layer {}) (width {}))\n'.format(x,y,x,y,layer,width)
  return string

def generate_BGA_footprint(dict_parameters,param_array):
  pitch = param_array[1]/100.0; n_ball_x = int(param_array[2])
  n_ball_y = int(param_array[3]); lenx = param_array[4]/100.0
  leny = param_array[5]/100.0

  outstring = "(module " + dict_parameters['name'] + ' (layer F.Cu)\n'      # module name
  outstring += '  (descr "'+dict_parameters['Description'] + '")\n'        # Description
  outstring += '  (tags "'+dict_parameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {0}) (layer F.SilkS)\n'.format(int(leny/2.+2))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dict_parameters['name'],int(leny/2.+2))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += draw_rect(lenx/2.,leny/2.,'F.SilkS')            # silkscreen rectangle
  outstring += draw_rect(lenx/2.+0.2,leny/2.+0.2,'F.CrtYd')    # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+0.5,leny/2.+0.5,lenx/2.+1,leny/2.+0.5)#silkscreen circle
  def create_pin_list(n_ball_x,n_ball_y):
      letter_BGA= ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','R','T','U','V','W','Y']
      pinlist = []
      for i in range(n_ball_x):
          for j in range(n_ball_y):
              firstletter = j/len(letter_BGA)
              defstr = ''
              if(firstletter != 0):
                  defstr = letter_BGA[firstletter-1]
              pinlist.append(defstr+letter_BGA[j-firstletter*len(letter_BGA)]+str(i+1))
      return pinlist
  
  pinlist = create_pin_list(n_ball_x,n_ball_y)
  minx = (n_ball_x-1)*pitch/2.; miny = (n_ball_y-1)*pitch/2.
  pn = 0 ; posx = -minx ; posy = -miny ; bsize = pitch/2.
  for pin in pinlist:
      if pn % n_ball_x == 0 and pn / n_ball_x != 0: # if we start a new column
          posx += pitch
          posy = -miny
      if abs(posx)<0.001: #avoid python precision issue
          posx = 0
      if abs(posy)<0.001: #avoid python precision issue
          posy = 0
      outstring += '  (pad {} smd circle (at {} {}) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(pin,posx,posy,bsize,bsize)
      posy += pitch
      pn += 1
  outstring += '  (model '+str(os.path.join(dict_parameters['3dModelPath'],dict_parameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring
      
def generate_QFN_footprint(dict_parameters,param_array):
  pitch = param_array[0]/100.0; lenx = param_array[1]/100.0; leny = param_array[2]/100.0; npins = int(param_array[4]); th_padx = param_array[5]/100.0; th_pady = param_array[6]/100.0
  outstring = "(module " + dict_parameters['name'] + ' (layer F.Cu)\n'      # module name
  outstring += '  (descr "' + dict_parameters['Description'] + '")\n'        # Description
  outstring += '  (tags "' + dict_parameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {}) (layer F.SilkS)\n'.format(int(leny/2.+4))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dict_parameters['name'], int(leny/2. + 4))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += draw_rect(lenx/2. + 0.1,leny/2.+ 0.1,'F.SilkS')            # silkscreen rectangle
  outstring += draw_rect(lenx/2. + pitch + 0.2,leny/2. + pitch + 0.2,'F.CrtYd')    # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2. + 1, leny/2. + 1, lenx/2. + 1, leny/2. + 0.5)#silkscreen circle
  quart_pin = npins/4; half_pin = npins/2; triquart_pin = 3*quart_pin
#  minx = (quart_pin+2)*pitch/2.; miny = (quart_pin+2)*pitch/2.
#FIXME pin #npin/8 shoud be y=0 #3*npin/8 should be x=0 etc
#this pad1x computation works only for square QFN
  test = npins/8.
  #if test % 2 == 0:
  pad1y = (test)*pitch - pitch/2
#  minx = (th_padx+0.2)/2. +3*pitch/4.; miny = (th_pady+0.2)/2.+3*pitch/4.
  minx = lenx/2.; miny = leny/2.
  posx = -minx ; posy = -pad1y ; psizex = pitch*1.5; psizey = pitch/1.5 
  for pin in range(npins):
      if pin < quart_pin:
          #posx = -minx
          if pin != 0:
            posy += pitch
      elif pin == quart_pin:
          posx = -pad1y
          posy = miny
          psizex = pitch/1.5
          psizey = pitch*1.5
      elif pin < half_pin:
          #posy = miny
          posx += pitch
      elif pin == half_pin:
          posy = pad1y
          posx = minx
          psizex = pitch*1.5
          psizey = pitch/1.5
      elif pin < triquart_pin:
          #posx = minx
          posy -= pitch
      elif pin == triquart_pin:
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
  outstring += '  (pad EPAD smd rect (at 0 0) (size {} {}) (layers F.Cu F.Paste F.Mask))\n'.format(th_padx+0.2,th_pady+0.2)
  outstring += '  (model '+str(os.path.join(dict_parameters['3dModelPath'],dict_parameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring


def generate_QFP_footprint(dict_parameters,param_array):
#FIXME figure out if dimension is actual lead span or body dimension
  pitch = param_array[0]/100.0; lenx = param_array[1]/100.0; leny = param_array[2]/100.0; npins = int(param_array[4])
  nomsizex = 1.5; nomsizey = pitch-0.1
  outstring = "(module " + dict_parameters['name'] + ' (layer F.Cu)\n'      # module name
  outstring += '  (descr "'+dict_parameters['Description'] + '")\n'        # Description
  outstring += '  (tags "'+dict_parameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {}) (layer F.SilkS)\n'.format(int(leny/2.+4))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dict_parameters['name'],int(leny/2.+4))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += draw_rect(lenx/2.,leny/2.,'F.SilkS')            # silkscreen rectangle
  outstring += draw_rect(lenx/2.+nomsizex,leny/2.+nomsizex,'F.CrtYd')            # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+1,leny/2.+1,lenx/2.+1,leny/2.+0.5)#silkscreen circle
  quart_pin = npins/4; half_pin = npins/2; triquart_pin = 3*quart_pin
#  minx = (quart_pin+2)*pitch/2.; miny = (quart_pin+2)*pitch/2.
#FIXME pin #npin/8 shoud be y=0 #3*npin/8 should be x=0 etc
#this pad1x computation works only for square QFP
  test = npins/8.
  pad1y = (test)*pitch - pitch/2
  minx = (lenx+1.5)/2.; miny = (leny+1.5)/2.
  posx = -minx ; posy = -pad1y ; psizex = nomsizex; psizey = nomsizey
  for pin in range(npins):
      if pin < quart_pin:
          if pin != 0:
            posy += pitch
      elif pin == quart_pin:
          posx = -pad1y
          posy = miny
          psizex = nomsizey
          psizey = nomsizex
      elif pin < half_pin:
          posx += pitch
      elif pin == half_pin:
          posy = pad1y
          posx = minx
          psizex = nomsizex
          psizey = nomsizey
      elif pin < triquart_pin:
          posy -= pitch
      elif pin == triquart_pin:
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
  outstring += '  (model '+str(os.path.join(dict_parameters['3dModelPath'],dict_parameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring

def generate_SOP_footprint(dict_parameters,param_array):
#FIXME Check nominal pad size for common SOP/SOIC packages
  pitch = param_array[0]/100.0; lenx = param_array[1]/100.0; leny = param_array[2]/100.0; npins = int(param_array[3]);
  nomsizex = 2
  nomsizey = pitch-0.1
  outstring = "(module " + dict_parameters['name'] + ' (layer F.Cu)\n'     # module name
  outstring += '  (descr "'+dict_parameters['Description'] + '")\n'        # Description
  outstring += '  (tags "'+dict_parameters['keywords'] + '")\n'            # keywords
  outstring += '  (attr smd)\n'                                           # attribute
  outstring += '  (fp_text reference REF** (at 0 {}) (layer F.SilkS)\n'.format(int(leny/2.+4))  # reference
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += '  (fp_text value {} (at 0 -{}) (layer F.Fab)\n'.format(dict_parameters['name'],int(leny/2.+4))  # value
  outstring += '    (effects (font (size 1 1) (thickness 0.15)))\n'
  outstring += '  )\n'
  outstring += draw_rect(lenx/2.+0.1,leny/2.+0.1,'F.SilkS')            # silkscreen rectangle
  outstring += draw_rect(lenx/2.+pitch+0.2,leny/2.+pitch+0.2,'F.CrtYd')    # courtyard rectangle
  outstring += '  (fp_circle (center -{} -{}) (end -{} -{}) (layer F.SilkS) (width 0.15))\n'.format(lenx/2.+1,leny/2.+1,lenx/2.+1,leny/2.+0.5)#silkscreen circle
  half_pin = npins/2
  test = npins/4.
  pad1y = (test)*pitch - pitch/2
  minx = (lenx+nomsizex)/2.; miny = (leny+nomsizex)/2.
  posx = -minx ; posy = -pad1y ; psizex = pitch*1.5; psizey = pitch/1.5 
  for pin in range(npins):
      if pin == 0:
        pass
      elif pin < half_pin:
          posy += pitch
      elif pin == half_pin:
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
  outstring += '  (model '+str(os.path.join(dict_parameters['3dModelPath'],dict_parameters['name']+'.wrl'))+'\n    (at (xyz 0 0 0))\n    (scale (xyz 1 1 1))\n    (rotate (xyz 0 0 0))\n  )\n'
  outstring += ')'
  
  return outstring
