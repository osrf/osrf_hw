#!/bin/bash

DIRECTORYTEST="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIRECTORYTEST
set -o errexit
set -o verbose
rm -rf $1
mkdir $1
cp gerbers/* README.txt stackup.pdf $1
cp "$(basename $DIRECTORYTEST)".csv $1/bill_of_materials.csv
rm -f $1.zip
zip -r $1.zip $1
