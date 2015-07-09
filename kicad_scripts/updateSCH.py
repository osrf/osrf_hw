#!/usr/bin/env python

import csv
import os
import sys

#FIXME: Pair stuff is very messy
def findBloc(string, keyword):
    keyword = keyword[0].upper() + keyword[1:].lower()
    idx = string.find('$'+keyword)
    if idx == -1:
        return [-1,-1]
    else:
        return [idx, idx + string[idx:].find('$End'+keyword) + len('$End'+keyword)+1]

def csv2Sch(bomfile,schfile):
    dictName = {}; compdict = {}; res = False
    if not os.path.isfile(bomfile):
        print 'BOM file ' + bomfile + 'doesnt exist'
        return res
    if not os.path.isfile(schfile):
        print 'SCH file ' + schfile +' doesnt exist'
        return res
    if not schfile.endswith('.sch'):
        print 'schematic file ' + schfile + ' is not a .sch file'
        return res
    with open(bomfile,'r') as bf, open(schfile,'r') as schr:
        reader = csv.reader(bf,delimiter=',', quotechar="'")
        # get column names from first row
        for row in reader:
            row = [x for x in row if x != '']
            for i in range(len(row)):
                if(i>4):
                    dictName[row[i]] = str(i-1)
            break
        #get every component from remaining rows
        for rows in reader:
            ll = []
            for i in range(len(rows)):
                if i != 0:
                    ll.append(rows[i])
            compdict[rows[0]]=ll
    
        sch = schr.read()
        schTemp = sch
        idx1=0;idx2=0;currentidx=0
        while schTemp != '':
            [idx1,idx2] = findBloc(schTemp,'Comp')
            if idx1 == -1:
                break
            else:
                skipcomponent = False
                compSch = schTemp[idx1:idx2]
                compSchTemp = compSch
                idxLine = 0
                # modify compSchTemp with the new values
                idxLine = compSchTemp.find('\n')+1
                # adding first line to lines string
                lines = ''
                line = compSchTemp[0:idxLine]
                while compSchTemp != '' or idxLine!=-1:
                    idxLine = compSchTemp.find('\n')
                    if idxLine == -1:
                        break
                    line = compSchTemp[0:idxLine]
                    compSchTemp = compSchTemp[idxLine+1:]
                    if skipcomponent == False:
                        if line.startswith('U'):
                            linelist = line.split(' ')
                            ID = linelist[-1]
                        elif line.startswith('F'):
                            pair = []
                            line2=line
                            idxq1=0;idxq2=0
                            # find " to escape spaces inside quotes
                            while idxq1 !=-1:
                                idxq1 = line2.find('"')
                                idxq2 = idxq1+1 + line2[idxq1+1:].find('"')
                                line2 = line2[idxq2+1:]
                                if(idxq1 != -1 and idxq2 != -1):
                                    if pair != []:
                                        pair.append([pair[-1][1] + idxq1, pair[-1][1] + idxq2+1])
                                    else:
                                        pair.append([idxq1, idxq2])
                                    
                            # perform space based separation
                            linelist = line[0:pair[0][0]].split(' ')
                            #generate list with all resulting elements
                            for i in range(len(pair)):
                                linelist.append(line[pair[i][0]:pair[i][1]+1])
                                try:
                                    templist =  line[pair[i][1]+1:pair[i+1][0]].split(' ')
                                    for elt in templist:
                                        linelist.append(elt)
                                except IndexError:
                                    templist = line[pair[i][1]+1:].split(' ')
                                    for elt in templist:
                                        linelist.append(elt)
                            linelist = [x for x in linelist if x != '']
                            key = linelist[-1]
                            if linelist[2].startswith('"#'):
                                skipcomponent = True
                            else:
                                if key.startswith('"'):
                                    #use dico
                                    value = compdict[ID][int(dictName[key[1:-1]])]
                                else:
                                    #get f number
                                    value = compdict[ID][int(linelist[1])]
                                line = line.replace(linelist[2],value)
                    lines += line + '\n'
                # replace in sch
                sch = sch.replace(compSch,lines)
                # update index and loop
                currentidx += len(lines)
                schTemp = sch[currentidx:]
    
    with open(schfile + '.TMP','w+') as schw:
        schw.write(sch)
        res = True
    return res
