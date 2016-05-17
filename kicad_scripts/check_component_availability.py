#!/usr/bin/env python

from __future__ import print_function
import csv
import os
import sys
import urllib2

def import_csv(filename):
    if not os.path.isfile(filename):
        print('pinfile not found')
        return
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        part_dict = {rows[5]:rows[8] for rows in reader}
    return part_dict

def check_availability(url, website):
    webpage = urllib2.urlopen(url)
    content = webpage.read()
    if website == 'digikey':
        str_qty = 'Digi-Key Stock: '  # quantityAvailable":"'
        idx = content.find(str_qty)
        if idx == -1:
          return 0
        idx2 = content[idx + len(str_qty):].find(' ')
        result = content[idx + len(str_qty):idx + len(str_qty) + idx2]
        result = result.replace(',','')
    elif website == 'mouser':
        str_qty = '  Can Ship Immediately'
        idx = content.find(str_qty)
        print('idx: {}'.format(idx))
        if idx == -1:
          return -1
        idx2 = content[:str_qty].rfind('\n')
        result = content[idx2:idx]
    else:
      return -1
    return int(result)

if len(sys.argv) != 2:
  print('invalid number of arguments')
  sys.exit()
if not os.path.isfile(sys.argv[1]):
    print('BOM file {} does not exist'.format(sys.argv[1]))
    sys.exit()

filepath = sys.argv[1]
dictionary = import_csv(filepath)
unavailable_components = []
for mfp, url in dictionary.items():
    qty = -1
    if not mfp in ['MFP', 'DNP']:
        print('poking {}'.format(url))
        if url.find('digikey.com') != -1:
            qty = check_availability(url, 'digikey')
        # FIXME not working for mouser for now
        # elif url.find('mouser.com') != -1:
        #     qty = check_availability(url, 'mouser')
        if qty <= 1:
            unavailable_components.append(mfp)
        print('checked availability of {}: {} remaining'.format(mfp, qty))
print(unavailable_components)
