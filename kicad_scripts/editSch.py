#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function
import csv
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os
import sys
from PyQt4 import QtGui, QtCore, Qt 
from sch.sch import *

#BUGS supports only copy past of block cells not isolated cells
#TODO Retest inside kicad
#TODO Resolve paths(every path relative to ws path)
#TODO Sort designator considering numerical values(C1,C10,...,C19,C2)--> (C1,C2,...C9,C10)
#TODO Undo function: meaning bufferize each new selected cell
def getRow(index):
    return index.row()
def getCol(index):
    return index.column()

class BOMEditor(QtGui.QWidget):
    def __init__(self, fileName = None, fileOut = None, mode='edit', parent=None):
        super(BOMEditor, self).__init__(parent)
        if fileName == None:
            filename = os.getcwd()
        else:
            self.fileName = fileName
        self.mode= 'edit'
        if fileOut == None:
            self.fileOut = fileName
        else:
            self.fileOut = fileOut
        if mode == None or mode == '':
            self.mode = 'edit'
        else:
            self.mode = mode
        self.model = QtGui.QStandardItemModel(self)
        self.sortOrder = 1 

        print('edition mode')
        ############################
        #### Action Management #####
        ############################
        self.actionQuit = QtGui.QAction(self)
        self.actionQuit.setObjectName('actionQuit')
        self.actionQuit.triggered.connect(QtGui.qApp.quit)
        self.actionQuit.setShortcut('Ctrl+Q')

        self.actionCopy = QtGui.QAction(self)
        self.actionCopy.setObjectName('actionCopy')
        self.actionCopy.triggered.connect(self.copy)
        self.actionCopy.setShortcut('Ctrl+C')

        self.actionPaste = QtGui.QAction(self)
        self.actionPaste.setObjectName('actionPaste')
        self.actionPaste.triggered.connect(self.paste)
        self.actionPaste.setShortcut('Ctrl+V')
        
        self.actionOpen = QtGui.QAction(self)
        self.actionOpen.setObjectName('actionOpen')
        self.actionOpen.triggered.connect(self.load)
        self.actionOpen.setShortcut('Ctrl+O')

        self.actionSave = QtGui.QAction(self)
        self.actionSave.setObjectName('actionSave')
        self.actionSave.triggered.connect(self.saveCsvSlot)
        self.actionSave.setShortcut('Ctrl+E')

        self.actionSaveSch = QtGui.QAction(self)
        self.actionSaveSch.setObjectName('actionSaveSCH')
        self.actionSaveSch.triggered.connect(self.saveSchSlot)
        self.actionSaveSch.setShortcut('Ctrl+S')

        self.actionAddRow = QtGui.QAction(self)
        self.actionAddRow.setObjectName('actionAddRow')
        self.actionAddRow.triggered.connect(self.insertRow)
        self.actionAddRow.setShortcut('Ctrl+N')

        self.actionDelete = QtGui.QAction(self)
        self.actionDelete.setObjectName('actionDelete')
        self.actionDelete.triggered.connect(self.deleteCells)
        self.actionDelete.setShortcut('Delete')

        self.actionDeleteRow = QtGui.QAction(self)
        self.actionDeleteRow.setObjectName('actionDeleteRow')
        self.actionDeleteRow.triggered.connect(self.deleteRows)
        self.actionDeleteRow.setShortcut('Ctrl+Shift+N')

#        self.actionUndo = QtGui.QAction(self)
#        self.actionUndo.setObjectName('actionUndo')
#        self.actionUndo.triggered.connect(self.undo)
#        self.actionUndo.setShortcut('Ctrl+Z')

        self.actionHelp = QtGui.QAction(self)
        self.actionHelp.setObjectName('actionHelp')
        self.actionHelp.triggered.connect(self.help)
        self.actionHelp.setShortcut('?')

        self.actionUpdateDB = QtGui.QAction(self)
        self.actionUpdateDB.setObjectName('actionUpdateDB')
        self.actionUpdateDB.triggered.connect(self.updateFromDB)
        self.actionUpdateDB.setShortcut('F5')

#        self.addAction(self.actionUndo)
        self.addAction(self.actionHelp)
        self.addAction(self.actionDelete)
        self.addAction(self.actionDeleteRow)
        self.addAction(self.actionAddRow)
        self.addAction(self.actionQuit)
        self.addAction(self.actionCopy)
        self.addAction(self.actionPaste)
        self.addAction(self.actionOpen)
        self.addAction(self.actionSave)
        self.addAction(self.actionSaveSch)
        self.addAction(self.actionUpdateDB)

        self.tableView = QtGui.QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.header = self.tableView.horizontalHeader()

        self.pushButtonLoad = QtGui.QPushButton(self)
        self.pushButtonLoad.setText("Load BOM/SCH (Ctrl+O)")
        self.pushButtonLoad.clicked.connect(self.load)

        self.pushButtonBOM = QtGui.QPushButton(self)
        self.pushButtonBOM.setText("Export BOM (Ctrl+E)")
        self.pushButtonBOM.clicked.connect(self.saveCsvSlot)

        self.pushButtonSCH = QtGui.QPushButton(self)
        self.pushButtonSCH.setText("Update/Save SCH (Ctrl+S)")
        self.pushButtonSCH.clicked.connect(self.saveSchSlot)

        self.pushButtonDB = QtGui.QPushButton(self)
        self.pushButtonDB.setText("DB autofill")
        self.pushButtonDB.clicked.connect(self.updateFromDB)

        self.layoutVertical = QtGui.QVBoxLayout(self)
        self.layoutHorizontal = QtGui.QHBoxLayout(self)

        self.layoutVertical.addWidget(self.tableView)
        self.layoutHorizontal.addWidget(self.pushButtonLoad)
        self.layoutHorizontal.addWidget(self.pushButtonBOM)
        self.layoutHorizontal.addWidget(self.pushButtonSCH)
        self.layoutHorizontal.addWidget(self.pushButtonDB)
        self.layoutVertical.addLayout(self.layoutHorizontal)

        self.header.sectionClicked.connect(self.onSectionClicked)
        
#        self.tableView.setFont(QtGui.QFont('Courier', 10, QtGui.QFont.Bold))
        if self.mode == 'edit':
            if fileName.lower().endswith('sch'):
                self.loadSch(self.fileName)
            elif fileName.lower().endswith('xml'):
                self.loadSch(self.fileName[:-3]+'sch')
            else:
                self.loadCsv(self.fileName)
    
            self.cb = QtGui.QApplication.clipboard()
            self.showMaximized()
        elif self.mode == 'generate':
            if self.fileName.lower().endswith('xml'):
                self.fileName = self.fileName[:-3]+'sch'
            if not os.path.isfile(self.fileName):
                print('Sch file doesnt exist')
                return
            self.loadSch(self.fileName)
            self.saveCsv(self.fileOut)
            sys.exit()
        else:
            print('"' + self.mode + '"is not a known mode')

                           

    def help(self):
        qmbox = QtGui.QMessageBox()
        qmbox.setText('<font face="Courier New"><b><u>List of HotKeys:</u></b><br><br>'\
                        '?:             Display Help<br>'\
                        'Ctrl+Q:        Exit application<br>'\
                        '<br><u>File Management</u><br>'\
                        'Ctrl+O:        Open an existing file (CSV or SCH)<br>'\
                        'Ctrl+S:        Save changes in an existing Schematic file<br>'\
                        'Ctrl+E:        Export table as CSV file<br>'\
                        '<br><u>Edition</u>:<br>'\
                        'Ctrl+C:        Copy selection to clipboard<br>'\
                        'Ctrl+V:        Paste clipboard content<br>'\
                        'Del:           Replace content of selection by "_" character<br>'\
                        'Ctrl+N:        Create a new Row below<br>'\
                        'Ctrl+Shift+N:  Delete selected Row(s)<br>'\
                        '<br><u>DB Actions:</u><br>'\
                        'F5:            Update table from DataBase<br>'\
                        '</font>'
                     )
        qmbox.setWindowTitle('Help')
        qmbox.exec_()

    ############################
    ## Cell Edition Functions ##
    ############################
#TODO
#    def undo(self):

    def deleteCells(self):
        selection = self.tableView.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            self.model.setData(idx,'_')

    def insertRow(self):
        selection = self.tableView.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            row = getRow(idx) + 1
            self.model.insertRow(row)
            for i in range(self.model.columnCount()):
                    self.model.setData(self.model.index(row,i),'_')

    def deleteRows(self):
        selection = self.tableView.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            self.model.removeRow(idx.row())

    def copy(self):
        outtext = ''
        selection = self.tableView.selectionModel()
        unsortedIndexes = selection.selectedIndexes()
        indexes = sorted(unsortedIndexes,key=getRow)
        previous = indexes[0]
        first = True
        for idx in indexes:
            dataVariant = self.model.data(idx)
            datastr = str(dataVariant)
            if not first:
                if idx.row() != previous.row():
                    outtext += '\n'
                else:
                    outtext += '\t'
            else:
                first = False
            outtext += datastr
            previous = idx
        self.cb.setText(outtext)

    def paste(self):
        selection = self.tableView.selectionModel()
        unsortedIndexes = selection.selectedIndexes()
        indexes = sorted(sorted(unsortedIndexes,key=getCol),key=getRow)
        row = indexes[0].row() 
        col0 = indexes[0].column()
        # split lines
        lines = self.cb.text().split('\n')

        for line in lines:
            col = col0
            linelist = line.split('\t')
            # split column on each line
            for elt in linelist:
                if(row < self.model.rowCount and col < self.model.columnCount):
                    idx = self.model.index(row,col)
                    #paste current cell and go to right cell
                    self.model.setData(idx,elt)
                col += 1
            row += 1
        return 

    #################################
    ## Column Management Functions ##
    #################################
    @QtCore.pyqtSlot(int)
    def onSectionClicked(self, clnNum):
        # First row stay always firs row
        llist = []
        for col in range(self.model.columnCount()):
            llist.append(str(self.model.data(self.model.index(0,col),
                QtCore.Qt.DisplayRole)))
        self.model.removeRow(0)
        self.sortOrder = 1 - self.sortOrder
        self.tableView.sortByColumn(clnNum,self.sortOrder)
        self.model.insertRow(0)
        for col in range(len(llist)):
            idx = self.model.index(0,col)
            self.model.setData(idx,llist[col])

    
    #################################
    ####### AutoFill Functions ######
    #################################
    def updateFromDB(self):
        #find column number for each param
        # DBFORMAT: KEY, Footprint, Datasheet, MFN, MFP, D1PN, D1PL, D2PN, D2PL
        keyGen = []
        dicParam = {}
        #FIXME comply to IEEE 315-1975 ?? https://en.wikipedia.org/wiki/Reference_designator
        classDico = {'C':'CAPA','D':'DIOD','FB':'BEAD','R':'RES','L':'INDU','U':'IC','P':'CONN','J':'CONN','Y':'XTAL', 'SW':'BUTN'}
        classFiles = {'C':'capacitors.csv','D':'diodes.csv','FB':'beads.csv','R':'resistors.csv','L':'inductors.csv','U':'ICs.csv','P':'connectors.csv','J':'connectors.csv','Y':'crystals.csv', 'SW':'switches.csv'}

        keyComp = '' ; compClass = ''
        desigIdx = -1
        for col in range(self.model.columnCount()):
            if str(self.model.data(self.model.index(0, col),
                    QtCore.Qt.DisplayRole )) == 'Designator':
                    desigIdx = col
            else:
                dicParam[str(self.model.data(self.model.index(0, col),
                    QtCore.Qt.DisplayRole ))] = col
        title = True
        for curRow in range(self.model.rowCount()):
            if title:
                title = False
                continue
            prevClass = compClass
            compClass = ''
            for key in classDico:
                if str(self.model.data(self.model.index(curRow,desigIdx),
                        QtCore.Qt.DisplayRole)).startswith(key):
                    compClass = classDico[key]
            if compClass == '':
                print('not complete')
                continue

##Voltage	Power	Tolerance	Temperature	ReverseVoltage	ForwardVoltage	Cont.Current	Frequency	Impedance(Peak)	ResonnanceFreq
            if compClass != prevClass:
                first = True
                # create keyDico
                if compClass == classDico['C']:
                    # keyFormat is CAPA_VALUE_PACKAGE_VOLTAGE_TOLERANCE_TEMPERATURE
                    keyGen = ['Value','Package','Voltage','Tolerance','Temperature']
                elif compClass == classDico['D']:
#                    # keyFormat is DIOD_VALUE_PACKAGE_FORWARDVOLTAGE_REVERSEVOLTAGE_CONTINUOUSCURRENT
                    keyGen = ['Value','Package','ForwardVoltage','ReverseVoltage','Cont.Current']
                elif compClass == classDico['FB']:
                    #FIXME Here value is impedance at frequency.
                    # keyFormat is BEAD_VALUE_PACKAGE_FREQUENCY_CONTINUOUSCURRENT
                    keyGen = ['Value','Package','Frequency','Cont.Current']
                elif compClass == classDico['R']:
                    # keyFormat is RES_VALUE_PACKAGE_POWER_TOLERANCE
                    keyGen = ['Value','Package','Power','Tolerance']
                elif compClass == classDico['L']:
                    # keyFormat is INDU_VALUE_PACKAGE_CONT.CURRENT_RESONNANCEFREQ
                    keyGen = ['Value','Package','Cont.Current','ResonnanceFreq']
                elif compClass == classDico['U']:
                    # keyFormat is IC_VALUE_PACKAGE
                    keyGen = ['Value','Package']
                elif compClass == classDico['J'] or compClass == classDico['P']:
                    # keyFormat is CONN_VALUE_PACKAGE
                    keyGen = ['Value','Package']
                elif compClass == classDico['Y']:
                    # keyFormat is XTAL_VALUE_PACKAGE
                    #FIXME Chose if value is the frequency or the reference of the component
                    keyGen = ['Value','Package']
                elif compClass == classDico['SW']:
                    # keyFormat is BUTN_VALUE_PACKAGE
                    keyGen = ['Value']
                else:
                    continue

                # set filename according to class
                for key,value in classDico.iteritems():
                    if value == compClass:
                        fileName = os.path.join(os.getcwd(),'db_files',classFiles[key])

                keyGenIdx = {}
                dbParamList = {}
                # create dico of parameters necessary to create key
                for col in range(self.model.columnCount()):
                    for i in range(len(keyGen)):
                        if str(self.model.data(self.model.index(0, col),
                            QtCore.Qt.DisplayRole )) == keyGen[i]:
                                keyGenIdx[str(i)] = col 
                                # set background to green to show that a value is expected in this cell
                                if str(self.model.data(self.model.index(curRow, col),QtCore.Qt.DisplayRole)) == '_':
                                    color = QtCore.Qt.red
                                else:
                                    color = QtCore.Qt.darkGreen
                                self.model.setData(
                                    self.model.index(curRow, col),
                                    QtGui.QColor(color),
                                    QtCore.Qt.BackgroundColorRole
                                    )
                                self.model.setData(
                                    self.model.index(curRow, col),
                                    QtGui.QColor(QtCore.Qt.white),
                                    QtCore.Qt.TextColorRole
                                    )
                                self.model.setData(
                                    self.model.index(0, col),
                                    QtGui.QColor(QtCore.Qt.darkGreen),
                                    QtCore.Qt.BackgroundColorRole
                                    )
                                self.model.setData(
                                    self.model.index(0, col),
                                    QtGui.QColor(QtCore.Qt.white),
                                    QtCore.Qt.TextColorRole
                                    )
            else:
                first = False
                for k in keyGenIdx:
                    if str(self.model.data(self.model.index(curRow, keyGenIdx[k]),QtCore.Qt.DisplayRole)) == '_':
                        color = QtCore.Qt.red
                    else:
                        color = QtCore.Qt.darkGreen
                    self.model.setData(
                        self.model.index(curRow, keyGenIdx[k]),
                        QtGui.QColor(color),
                        QtCore.Qt.BackgroundColorRole
                        )
                    self.model.setData(
                        self.model.index(curRow, keyGenIdx[k]),
                        QtGui.QColor(QtCore.Qt.white),
                        QtCore.Qt.TextColorRole
                        )
                    

            if len(keyGen) > len(keyGenIdx):
                print('Missing parameters in you sch file')
                continue
            if not (fileName !='' and os.path.isfile(fileName)):
                continue
            keyComp = compClass
#            keyFail = False
            # create key
            for i in range(len(keyGenIdx)):
                temp = str(self.model.data(self.model.index(curRow,\
                           keyGenIdx[str(i)]),QtCore.Qt.DisplayRole))
#                if temp != '_' and temp != '':
                keyComp += '_' + str(self.model.data(self.model.index(curRow,\
                                         keyGenIdx[str(i)]),QtCore.Qt.DisplayRole))
#                else:
#                    keyFail = True
#            if keyFail == True:
#                continue
            #print('new dbKey is :' + keyComp)
            # openfile 
            with open(fileName, "rb") as fileInput:
            # create dbParamlist from first row
                first = True
                for row in csv.reader(fileInput):    
                    if first:
                        for j in range(len(row)):
                            if row[j] != '' and row[j] != 'KEY':
                                dbParamList[row[j]] = j 
                        first = False
                        #print(dbParamList)
                    else:
                        if row[0]==keyComp:
                            #update table
                            for key in dbParamList:
                                try:
                                    self.model.setData(self.model.index(curRow,dicParam[key]),row[int(dbParamList[key])])
                                except:
                                    pass

    ###############################
    ## File Management Functions ##
    ###############################

    def load(self):
        path = os.getcwd()
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',os.path.dirname(self.fileName), "*.csv *.sch")
        print(fname)
        if fname.lower().endswith('sch'):
            self.loadSch(fname)
        else:
            self.loadCsv(fname)

    def loadCsv(self, fileName):
        if fileName !='' and os.path.isfile(fileName):
            self.model.removeRows(0, int(self.model.rowCount()))
            with open(fileName, "rb") as fileInput:
                print('loading csv')
                for row in csv.reader(fileInput):    
                    items = [
                        QtGui.QStandardItem(field)
                        for field in row
                    ]
                    self.model.appendRow(items)

    def loadSch(self,fname):
        if not (os.path.isfile(fname) and fname.endswith('.sch')):
            sys.exit(0)
        dictComponent = {'0':'Designator',
                         '1':'Value',
                         '2':'Footprint',
                         '3':'Datasheet',
                        }
        self.addCompToTable(fname,dictComponent)

    def addCompToTable(self, filename, dictComponent,firstRow=True):
        columnOrder = {}
        sch = Schematic(filename)
        first = True
        for comp in sch.components:
            if '#PWR' in comp.labels['ref']:
                continue
            if first:
                i = 1
                compRow0 = []
                compRow0.append(QtGui.QStandardItem('ID'))
                columnOrder['ID'] = 0
                for field in comp.fields:
                    if field['name'] == '':
                        compRow0.append(QtGui.QStandardItem(dictComponent[field['id']]))
                        columnOrder[field['id']] = i
                    else:
                        compRow0.append(QtGui.QStandardItem(field['name'][1:-1]))
                        columnOrder[field['name'][1:-1]] = i
                    i+=1
                if firstRow:
                    self.model.appendRow(compRow0)
                    firstRow = False
                first = False

            compRow = []
            for i in range(len(compRow0)):
                compRow.append('_')
            compRow[0] = comp.unit['time_stamp']
            for field in comp.fields:
                if field['name'] == '':
                    compRow[columnOrder[field['id']]] = field['ref'][1:-1]
                elif field['name'][1:-1] == '':
                    continue
                else:
                    try:
                        compRow[columnOrder[field['name'][1:-1]]] = field['ref'][1:-1]
                    except KeyError:
                        pass
            self.model.appendRow([ QtGui.QStandardItem(x) for x in compRow])

        for sh in sch.sheets:
            for field in sh.fields:
                if field['id'] == 'F1':
                    if field['value'].find('.sch')!= -1:
                        sheetname = field['value'][1:-1]
            sheetname = os.path.join(os.path.dirname(filename),sheetname)
            self.addCompToTable(sheetname,dictComponent,False)

    def saveSch(self,fname):
        sch = Schematic(fname)
        for sh in sch.sheets:
            for field in sh.fields:
                if field['id'] == 'F1':
                    if field['value'].find('.sch')!= -1:
                        sheetname = field['value'][1:-1]
                        sheetname = os.path.join(os.path.dirname(fname),sheetname)
                        self.saveSch(sheetname)
        for row in range(self.model.rowCount()):
            for comp in sch.components:
                if not str(comp.unit['time_stamp']) == str(self.model.data(self.model.index(row,0),
                QtCore.Qt.DisplayRole)):
                    continue
                for col in range(self.model.columnCount()):
                    for field in comp.fields:
                        compareField = ''
                        if field['name'] != '':
                            compareField = field['name'][1:-1]
                        if self.model.data(self.model.index(0,col),QtCore.Qt.DisplayRole) == compareField:
#FIXME
#Update only if necessary: Worth it ?
#                            if field['ref'] != '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"':
                            field['ref'] = '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"'
                        elif col<= 4:
                            if field['id'] == str(col-1):
#                                if field['ref'] != '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"':
                                field['ref'] = '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"'
        sch.save()
            
    @QtCore.pyqtSlot()
    def saveSchSlot(self):
        print('SCH Saved')
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Update SCH file', os.path.dirname(self.fileName), "*sch")
        if not os.path.isfile(fname):
            print('ERROR Schematic file not found')
            return
        self.saveSch(fname)

    @QtCore.pyqtSlot()
    def saveCsvSlot(self):
        path = os.path.dirname(self.fileName)
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save BOM', path, "*.csv")
        print(fname)
        if fname != '':
            self.saveCsv(fname)

    def saveCsv(self, fileName):
        print('filename=' + fileName)
        with open(fileName, "wb") as fileOutput:
            writer = csv.writer(fileOutput,delimiter=',',quotechar="'")
            for rowNumber in range(self.model.rowCount()):
                fields=[]
                for columnNumber in range(self.model.columnCount()):
                    a = str(self.model.data(self.model.index(rowNumber, columnNumber),
                        QtCore.Qt.DisplayRole ))
                    if len(a)>0:
                        if columnNumber != 0:
                            if a[0]!='"':
                                a = '"' + str(a) + '"'
                        fields.append(a)
                    else:
                        a = '""'
                        fields.append(a)
                writer.writerow(fields)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('BOM editor')
    args = app.arguments()
    outfilepath = ''; infilepath = ''; mode=''
    if len(args)>2:
        if len(args)>3:
            mode = args[3]
        infilepath = args[1]
        outfilepath = args[2]
    elif len(args)==2:
        infilepath = args[1]
        
    main = BOMEditor(infilepath,outfilepath,mode)
    main.show()

    sys.exit(app.exec_())
