#!/usr/bin/env python

from __future__ import print_function
import glob
import os
import sys

if not len(sys.argv) == 2:
  print('wrong number of arguments')
  sys.exit()
if not (os.path.isdir(sys.argv[1]) and sys.argv[1].endswith('.pretty')):
  print('{} is not a valid kicad module library path (.pretty folder)')
  sys.exit()

directory = sys.argv[1]

for filename in glob.glob(os.path.join(directory, '*.kicad_mod')):
  print('opening {}'.format(filename))
  with open(filename, "r+") as f:
    content = f.read()
    content = content.replace("*.Mask F.SilkS)", "*.Mask)")
    f.seek(0)
    f.write(content)
    f.truncate()
