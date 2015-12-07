#! /bin/bash

b="osrf_hw"
cd $1
pwd
DIRECTORYTEST=$1
libDirLine="LibDir=\${KISYSLIB}"

b="osrf_hw"
c="../../$b"
cc=$(find $1 -type f -name "*.pro")
for file in $cc
do
  cd "$( dirname $file)"
  rm *bak *.bck *.swp *-cache.lib
##DIRWORKSPACE=$( dirname "$DIRECTORYTEST")
  outString=""
  while IFS='' read -r line || [[ -n "$line" ]]; do
      if [[ $line == LibName* ]] && [[ $line == *osrf_hw* ]] && [[ $line != ../../osrf_hw* ]];
      then
        libnumber=${line%=*}
        line2=${line#*=}
        line3=${line2#*osrf_hw}
        line="$libnumber=$c$line3"
      fi
      if [[ $line == LibDir* ]] && [[ $line != $libDirLine ]];
      then
        line=$libDirLine
      fi
      outString=$outString"$line\n"
  done < $file
  echo -e $outString > $file 
done


#FIXME Chunk of code to find osrf_hw and workspace: useless because workspace structure is fixed
#DIRECTORYTEST="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#DIRSCRIPT=$DIRECTORYTEST
#DIRPROJECT=$1
#
##echo $1
##while [ "$( basename "$DIRECTORYTEST")" != "$b" ];do 
##  DIRECTORYTEST=$( dirname "$DIRECTORYTEST")
##done
##DIRWORKSPACE=$( dirname "$DIRECTORYTEST")
##echo "workspace directory: $DIRWORKSPACE"
##
##i=0
##while [ "$( dirname "$DIRPROJECT")" != "$DIRWORKSPACE" ];do 
##  i=$((i+1))
##  DIRPROJECT=$( dirname "$DIRPROJECT")
##done
##echo $DIRPROJECT
##echo $i
