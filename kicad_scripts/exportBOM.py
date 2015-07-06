#!/usr/bin/env python

import csv
#import argparse
import os
import sys

#parser = argparse.ArgumentParser()
#parser.add_argument('-f','--file', default=None, help='file to convert')
#
#args = parser.parse_args()
def findBloc(string, keyword):
    keyword = keyword[0].upper() + keyword[1:].lower()
    idx = string.find('$'+keyword)
    if idx == -1:
        return [-1,-1]
    else:
        return [idx, idx + string[idx:].find('$End'+keyword)]

def findSheets(filename):
    with open(filename, mode='r') as infile:
        content = infile.read()
        txt = content
        idxbeg =0;idxend=0
        sheetList = []

        while txt != '': # while there are still $Comp tags
            # find sheet blocs
            [idx1,idx2] = findBloc(txt,'Sheet')
            if idx1 == -1 :
                break
            else:
                idxend = idxbeg + idx2
                idxbeg += idx1

                sheetContent = content[idxbeg:idxend]
                txt = txt[idxend:]

                while sheetContent != '':
                    idx3 = sheetContent.find('\n')
                    line = sheetContent[0:idx3]
                    sheetContent = sheetContent[idx3+1:]
                    # extract the ID: we shouldn't need the ID
                    if line.startswith('U'):
                        linelist = line.split(' ')
                        ID = linelist[-1]
                    elif line.startswith('F'):
                        if line.find('.sch') != -1:
                            listt = line.split(' ')
                            for l in listt:
                                if l.find('.sch') != -1:
                                    sheetList.append(l[1:-1])
                                    sheetContent = ''
    return sheetList

def extractComponentList(filename,dictComponent):
    componentList = []
    with open(filename,mode='r') as infile:
        content = infile.read()
        component = 'aa'
        while component != '': # while there are still $Comp tags
            skipComponent = False
            currentComponent = {}
            #find component boundaries
            component ='df'
            [idx,idx2] = findBloc(content,'Comp')
            component = content[idx:idx2]
            content = content[idx2:]
            found = component
            line = 'df'
            # process line by line
            while line != '':
                idx3 = found.find('\n')
                line = found[0:idx3]
                found = found[idx3+1:]
                # locate the component unique ID
                if line.startswith('U'):
                    linelist = line.split(' ')
                    ID = linelist[-1]
                # retrieve all the data fields
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
                    #generate liste with all resulting elements
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

                    attribIdx = linelist[1]
                    attribVal = linelist[2]

                    if len(pair) > 1:
                        attribName = linelist[-1]
                        if not attribIdx in dictComponent:
                            dictComponent[attribIdx] = attribName[1:]
                    # Skip the power marker components
                    if attribVal.startswith('"#'):
                        skipComponent = True
                        break
                    else:
                        currentComponent[dictComponent[attribIdx]] = attribVal
            # add valid component to componentList
            if not skipComponent and currentComponent !={}:
                componentList.append(currentComponent)
                currentComponent['ID'] = ID

    return componentList

