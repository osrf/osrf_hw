#!/usr/bin/env python
#-*- coding:utf-8 -*-
import csv

import sip
import exportBOM as bom
import updateSCH as upSCH
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os
import sys
from PyQt4 import QtGui, QtCore, Qt 

#BUGS supports only copy past of block cells not isolated cells
#TODO Resolve paths(every path relative to ws path)
#TODO Undo function ? meaning buffer each new selected cell

def getRow(index):
    return index.row()
def getCol(index):
    return index.column()

class BOMEditor(QtGui.QWidget):
    def __init__(self, fileName = None, fileOut = None, mode='edit', parent=None):
        super(BOMEditor, self).__init__(parent)
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

        print 'edition mode'
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
        self.actionSave.triggered.connect(self.save)
        self.actionSave.setShortcut('Ctrl+S')

        self.actionSaveSch = QtGui.QAction(self)
        self.actionSaveSch.setObjectName('actionSaveSCH')
        self.actionSaveSch.triggered.connect(self.saveSch)
        self.actionSaveSch.setShortcut('Ctrl+Shift+S')

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

        self.actionHelp = QtGui.QAction(self)
        self.actionHelp.setObjectName('actionHelp')
        self.actionHelp.triggered.connect(self.help)
        self.actionHelp.setShortcut('?')

#        self.actionUndo = QtGui.QAction(self)
#        self.actionUndo.setObjectName('actionUndo')
#        self.actionUndo.triggered.connect(self.undo)
#        self.actionUndo.setShortcut('Ctrl+Z')
#
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

        self.tableView = QtGui.QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.header = self.tableView.horizontalHeader()

        self.pushButtonLoad = QtGui.QPushButton(self)
        self.pushButtonLoad.setText("Load BOM/SCH (Ctrl+O)")
        self.pushButtonLoad.clicked.connect(self.load)

        self.pushButtonBOM = QtGui.QPushButton(self)
        self.pushButtonBOM.setText("Save BOM (Ctrl+S)")
        self.pushButtonBOM.clicked.connect(self.save)

        self.pushButtonSCH = QtGui.QPushButton(self)
        self.pushButtonSCH.setText("Update SCH (Ctrl + Shift + S)")
        self.pushButtonSCH.clicked.connect(self.saveSchSlot)

        self.pushButtonDB = QtGui.QPushButton(self)
        self.pushButtonDB.setText("DB")
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

        if self.mode == 'edit':
            print 'edition mode'
            if fileName.lower().endswith('sch'):
                self.loadSch(self.fileName)
            elif fileName.lower().endswith('xml'):
                self.loadSch(self.fileName[:-3]+'sch')
            else:
                self.loadCsv(self.fileName)
    
            self.cb = QtGui.QApplication.clipboard()
#            print 'edition mode'
            self.showMaximized()
        elif self.mode == 'generate':
            if self.fileName.lower().endswith('xml'):
                self.fileName = self.fileName[:-3]+'sch'
            if not os.path.isfile(self.fileName):
                print 'Sch file doesnt exist'
                return
            self.loadSch(self.fileName)
            self.saveCsv(self.fileOut)
#            QtGui.qApp.quit()
            print 'conversion done'
            sys.exit()
        else:
            print  '"' + self.mode + '"is not a known mode'
            

    def help(self):
        #TODO Write Help Text
        print 'help function called'
        qmbox = QtGui.QMessageBox()
        qmbox.setText('blabla\nblabla\nblablabla')
        qmbox.setWindowTitle('Help')
        qmbox.exec_()

    ############################
    ## Cell Edition Functions ##
    ############################
#    def undo(self):

    def deleteCells(self):
        selection = self.tableView.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            self.model.setData(idx,'')

    def insertRow(self):
        self.model.insertRow(self.model.rowCount())

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

    
    def updateFromDB(self):
        #find column number for each param
        # DBFORMAT: KEY, Footprint, Datasheet, MFN, MFP, DigiPN, DigiPL, mouserPN, mouserPL
#        dbparamlist = {'KEY':'0', 'Footprint':'1', 'Datasheet':'2', 'MFN':'3',\
#                'MFP':'4', 'D1PN':'5', 'D1PL':'6', 'D2PN':'7', 'D2PL':'8'}
        keyGen = ['Designator','Value','Package']
        keyGenIdx = {} ; dicparam = {}
        dbParamList = {'KEY':'0', 'Footprint':'1', 'Datasheet':'2', 'MFN':'3','MFP':'4', 'D1PN':'5', 'D1PL':'6', 'D2PN':'7', 'D2PL':'8'}
        classDico = {'C':'CAPA','D':'DIOD','FB':'BEAD','R':'RES','L':'INDU','U':'IC','P':'CONN','J':'CONN','Y':'CLK', 'SW':'BUTN'}
        for col in range(self.model.columnCount()):
            for key in dbParamList:
                if str(self.model.data(self.model.index(0, col),
                    QtCore.Qt.DisplayRole )) == key:
                    dicparam[key] = col
            for i in range(len(keyGen)):
                if str(self.model.data(self.model.index(0, col),
                    QtCore.Qt.DisplayRole )) == keyGen[i]:
                        keyGenIdx[keyGen[i]] = col
        
        print dicparam
#        print keyGenIdx
        fileName = os.path.join(os.getcwd(),'db_0402_6.3V_capacitors.csv')
        print fileName
        if fileName !='' and os.path.isfile(fileName):
                for curRow in range(self.model.rowCount()):
                    keyComp = ''
                    for key in classDico:
                        if str(self.model.data(self.model.index(curRow,keyGenIdx['Designator']),
                                QtCore.Qt.DisplayRole)).startswith(key):
                            keyComp += classDico[key] + '_'
                    if keyComp == '':
                        print 'not complete'
                        continue
                    oldlen = len(keyComp)
                    keyComp += str(self.model.data(self.model.index(curRow,keyGenIdx['Value']),
                                QtCore.Qt.DisplayRole))
                    if len(keyComp) == oldlen:
                        print 'not complete'
                        continue
                    keyComp += '_'
                    oldlen = len(keyComp)
                    keyComp += str(self.model.data(self.model.index(curRow,keyGenIdx['Package']),
                                QtCore.Qt.DisplayRole))
                    if len(keyComp) <= oldlen +1 :
                        continue
#                    print keyComp

                    with open(fileName, "rb") as fileInput:
                        for row in csv.reader(fileInput):    
                            if row[0] == keyComp:
                                for key in dbParamList:
                                    try:
                                        self.model.setData(self.model.index(curRow,dicparam[key]),row[int(dbParamList[key])])
                                    except:
                                        pass

        else:
            print 'Database not found'

#            desigIdx = 
#FIXME
#        for rowNumber in range(self.model.rowCount()):
#            # generate key
#            key = ''
#            if str(self.model.data(self.model.index(rowNumber, dicparam[]),
#                        QtCore.Qt.DisplayRole ))



    ###############################
    ## File Management Functions ##
    ###############################
    @QtCore.pyqtSlot()
    def saveSchSlot(self):
        print('SCH Saved')
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Update SCH file', os.path.dirname(self.fileOut), "*sch")
        if not os.path.isfile(fname):
            print('ERROR Schematic file not found')
            return
        self.saveSch(fname)

    def saveSch(self, fname):
        # write temporary csv file
        tempfilename = fname[:-4] + '.tmpcsv2sch'
        self.saveCsv(tempfilename)
        # load it as dictionary and update SCH
        if not upSCH.csv2Sch(tempfilename,fname):
            print 'couldnt update SCH File'
            #remove temps files and leave SCH file unchanged
            os.remove(fname + '.TMP')
        else:
            # replace SCH file with updated one
            os.rename(fname + '.TMP', fname)
        os.remove(tempfilename)
        return

    def loadSch(self,fname):
        if not os.path.isfile(fname):
            print('file doesnt exist')
            return
#        print('Generating BOM from SCH file')
        dictComponent = {'0':'Designator',
                         '1':'Value',
                         '2':'Footprint',
                         '3':'Datasheet',
                        }
        # list of dictionaries, each dictionary is a component
        cList = []
        cList = bom.extractComponentList(fname,dictComponent)
        sheetStr = bom.findSheets(fname)

        for sh in sheetStr:
#            print 'processing ' + sh + ' sheet'
            cList += bom.extractComponentList(os.path.join(os.path.dirname(fname),sh),dictComponent)
        tmpCsvFile = fname + '.tmp'
        with open(tmpCsvFile,mode='w+') as fo:
            # create first line with column titles
            strout = 'ID(DO_NOT_CHANGE),'
            for i in range(len(dictComponent)):
                strout += dictComponent[str(i)] + ','
            strout += '\n'
            print dictComponent
            # add all component as lines
            for comp in cList:
                strout += comp['ID'] + ','
                for i in range(len(dictComponent)):
                    strout +=  comp[dictComponent[str(i)]] + ',' 
                strout += '\n'
            fo.write(strout)
        self.loadCsv(tmpCsvFile)
        os.remove(tmpCsvFile)
        

    def load(self):
        path = os.getcwd()
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',path, "*.csv *.sch")
        print fname
        if fname.lower().endswith('sch'):
            self.loadSch(fname)
        else:
            self.loadCsv(fname)

    def save(self):
        path = os.path.dirname(self.fileName)
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save BOM', path, "*.csv")
        print fname
        if fname != '':
            self.saveCsv(fname)

    def loadCsv(self, fileName):
        if fileName !='' and os.path.isfile(fileName):
            self.model.removeRows(0, int(self.model.rowCount()))
            with open(fileName, "rb") as fileInput:
                print 'loading csv'
                for row in csv.reader(fileInput):    
                    items = [
                        QtGui.QStandardItem(field)
                        for field in row
                    ]
                    self.model.appendRow(items)
        #remove empty column and sort table
#        self.model.removeColumn(self.model.columnCount()-1)
#        self.sortOrder = 1
#        self.onSectionClicked(1)

    def saveCsv(self, fileName):
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
#        print 'saved csv: ' + fileName

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
#        print outfilepath
    elif len(args)==2:
        infilepath = args[1]
        
    main = BOMEditor(infilepath,outfilepath,mode)
    main.show()

    sys.exit(app.exec_())
