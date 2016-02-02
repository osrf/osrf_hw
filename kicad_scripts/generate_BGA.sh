#! /bin/bash

# 1 parse config file
if [ -f $1 ];then
  while read line; do
    if [[ "$line" =~ ^[^#]*= ]]; then
      if [ ${line%%=*} = "name" ];then
        BGANAME="${line#*=}"
      elif [ ${line%%=*} = "outLibrary" ];then
        LIBRARYPATH="${line#*=}"
      elif [ ${line%%=*} = "3dModelPath" ];then
        STEPMODELPATH="${line#*=}"
      else
        :
      fi
    fi
  done < $1
  #2 launch generate_BGA_footprint.py
  ./generate_BGA_footprint.py $1
  #3 get BGA name + full path ?
  BGAFullpath="$STEPMODELPATH/$BGANAME.wrl"
  #4 launch freecad script according to BGA name
  freecad freecad_gen_BGA.py $BGAFullpath
fi

