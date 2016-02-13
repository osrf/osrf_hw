#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import print_function
import csv
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import re
import os
import sys
from PyQt4 import QtGui, QtCore, Qt
from sch.sch import *

#BUGS supports only copy past of block cells not isolated cells
#TODO Resolve paths(every path relative to ws path)
#TODO Sort designator considering numerical values(C1,C10,...,C19,C2)--> (C1,C2,...C9,C10)
#TODO Undo function: meaning bufferize each new selected cell
def get_row(index):
    return index.row()
def get_col(index):
    return index.column()

def safeint(x):
  try:
    return int(x)
  except ValueError:
    return x

class BOMEditor(QtGui.QWidget):
    def __init__(self, file_name = None, file_out = None, mode='edit', parent=None):
        super(BOMEditor, self).__init__(parent)
        if file_name == None:
            self.file_name = os.getcwd()
        else:
            self.file_name = file_name
        self.mode= 'edit'
        if file_out == None:
            self.file_out = file_name
        else:
            self.file_out = file_out
        if mode == None or mode == '':
            self.mode = 'edit'
        else:
            self.mode = mode
        self.model = QtGui.QStandardItemModel(self)
        self.sort_order = 1

        print('edition mode')
        ############################
        #### Action Management #####
        ############################
        self.action_quit = QtGui.QAction(self)
        self.action_quit.setObjectName('action_quit')
        self.action_quit.triggered.connect(QtGui.qApp.quit)
        self.action_quit.setShortcut('Ctrl+Q')

        self.action_copy = QtGui.QAction(self)
        self.action_copy.setObjectName('action_copy')
        self.action_copy.triggered.connect(self.copy)
        self.action_copy.setShortcut('Ctrl+C')

        self.action_paste = QtGui.QAction(self)
        self.action_paste.setObjectName('action_paste')
        self.action_paste.triggered.connect(self.paste)
        self.action_paste.setShortcut('Ctrl+V')

        self.action_open = QtGui.QAction(self)
        self.action_open.setObjectName('action_open')
        self.action_open.triggered.connect(self.load)
        self.action_open.setShortcut('Ctrl+O')

        self.action_save = QtGui.QAction(self)
        self.action_save.setObjectName('action_save')
        self.action_save.triggered.connect(self.save_csv_slot)
        self.action_save.setShortcut('Ctrl+E')

        self.action_save_sch = QtGui.QAction(self)
        self.action_save_sch.setObjectName('action_save_sch')
        self.action_save_sch.triggered.connect(self.save_sch_slot)
        self.action_save_sch.setShortcut('Ctrl+S')

        self.action_add_row = QtGui.QAction(self)
        self.action_add_row.setObjectName('action_add_row')
        self.action_add_row.triggered.connect(self.insert_row)
        self.action_add_row.setShortcut('Ctrl+N')

        self.action_delete = QtGui.QAction(self)
        self.action_delete.setObjectName('action_delete')
        self.action_delete.triggered.connect(self.delete_cells)
        self.action_delete.setShortcut('Delete')

        self.action_delete_row = QtGui.QAction(self)
        self.action_delete_row.setObjectName('action_delete_row')
        self.action_delete_row.triggered.connect(self.delete_rows)
        self.action_delete_row.setShortcut('Ctrl+Shift+N')

#        self.action_undo = QtGui.QAction(self)
#        self.action_undo.setObjectName('action_undo')
#        self.action_undo.triggered.connect(self.undo)
#        self.action_undo.setShortcut('Ctrl+Z')

        self.action_help = QtGui.QAction(self)
        self.action_help.setObjectName('action_help')
        self.action_help.triggered.connect(self.help)
        self.action_help.setShortcut('?')

        self.action_update_db = QtGui.QAction(self)
        self.action_update_db.setObjectName('action_update_db')
        self.action_update_db.triggered.connect(self.update_from_db)
        self.action_update_db.setShortcut('F5')

#        self.addAction(self.action_undo)
        self.addAction(self.action_help)
        self.addAction(self.action_delete)
        self.addAction(self.action_delete_row)
        self.addAction(self.action_add_row)
        self.addAction(self.action_quit)
        self.addAction(self.action_copy)
        self.addAction(self.action_paste)
        self.addAction(self.action_open)
        self.addAction(self.action_save)
        self.addAction(self.action_save_sch)
        self.addAction(self.action_update_db)

        self.table_view = QtGui.QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.header = self.table_view.horizontalHeader()

        self.push_button_load = QtGui.QPushButton(self)
        self.push_button_load.setText("Load BOM/SCH (Ctrl+O)")
        self.push_button_load.clicked.connect(self.load)

        self.push_button_BOM = QtGui.QPushButton(self)
        self.push_button_BOM.setText("Export BOM (Ctrl+E)")
        self.push_button_BOM.clicked.connect(self.save_csv_slot)

        self.push_button_SCH = QtGui.QPushButton(self)
        self.push_button_SCH.setText("Update/Save SCH (Ctrl+S)")
        self.push_button_SCH.clicked.connect(self.save_sch_slot)

        self.push_button_DB = QtGui.QPushButton(self)
        self.push_button_DB.setText("DB autofill")
        self.push_button_DB.clicked.connect(self.update_from_db)

        self.layout_vertical = QtGui.QVBoxLayout(self)
        self.layout_horizontal = QtGui.QHBoxLayout(self)

        self.layout_vertical.addWidget(self.table_view)
        self.layout_horizontal.addWidget(self.push_button_load)
        self.layout_horizontal.addWidget(self.push_button_BOM)
        self.layout_horizontal.addWidget(self.push_button_SCH)
        self.layout_horizontal.addWidget(self.push_button_DB)
        self.layout_vertical.addLayout(self.layout_horizontal)

        self.header.sectionClicked.connect(self.onSectionClicked)

#        self.table_view.setFont(QtGui.QFont('Courier', 10, QtGui.QFont.Bold))
        if self.mode == 'edit':
            if file_name.lower().endswith('sch'):
                self.load_sch(self.file_name)
            elif file_name.lower().endswith('xml'):
                self.load_sch(self.file_name[:-3]+'sch')
            else:
                self.load_csv(self.file_name)
            self.cb = QtGui.QApplication.clipboard()
            self.showMaximized()
        elif self.mode == 'generate':
            if self.file_name.lower().endswith('xml'):
                self.file_name = self.file_name[:-3]+'sch'
            if not os.path.isfile(self.file_name):
                print('Sch file doesnt exist')
                return
            self.load_sch(self.file_name)
            self.save_BOM(self.file_out)
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

    def delete_cells(self):
        selection = self.table_view.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            self.model.setData(idx,'_')

    def insert_row(self):
        selection = self.table_view.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            row = get_row(idx) + 1
            self.model.insertRow(row)
            for i in range(self.model.columnCount()):
                    self.model.setData(self.model.index(row,i),'_')

    def delete_rows(self):
        selection = self.table_view.selectionModel()
        indexes = selection.selectedIndexes()
        for idx in indexes:
            self.model.removeRow(idx.row())

    def copy(self):
        outtext = ''
        selection = self.table_view.selectionModel()
        unsorted_indexes = selection.selectedIndexes()
        indexes = sorted(unsorted_indexes,key=get_row)
        previous = indexes[0]
        first = True
        for idx in indexes:
            data_variant = self.model.data(idx)
            datastr = str(data_variant)
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
        selection = self.table_view.selectionModel()
        unsorted_indexes = selection.selectedIndexes()
        indexes = sorted(sorted(unsorted_indexes,key=get_col),key=get_row)
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
    def onSectionClicked(self, cln_num):
        # First row stay always firs row
        llist = []
        for col in range(self.model.columnCount()):
            llist.append(str(self.model.data(self.model.index(0,col),
                QtCore.Qt.DisplayRole)))
        self.model.removeRow(0)
        self.sort_order = 1 - self.sort_order
        self.table_view.sortByColumn(cln_num,self.sort_order)
        self.model.insertRow(0)
        for col in range(len(llist)):
            idx = self.model.index(0,col)
            self.model.setData(idx,llist[col])


    #################################
    ####### AutoFill Functions ######
    #################################
    def update_from_db(self):
        #find column number for each param
        # DBFORMAT: KEY, Footprint, Datasheet, MFN, MFP, D1PN, D1PL, D2PN, D2PL
        key_gen = []
        dic_param = {}
        #FIXME comply to IEEE 315-1975 ?? https://en.wikipedia.org/wiki/Reference_designator
        class_dico = {'C':'CAPA','D':'DIOD','FB':'BEAD','R':'RES','L':'INDU','U':'IC','P':'CONN','J':'CONN','Y':'XTAL', 'SW':'BUTN'}
        class_files = {'C':'capacitors.csv','D':'diodes.csv','FB':'beads.csv','R':'resistors.csv','L':'inductors.csv','U':'ICs.csv','P':'connectors.csv','J':'connectors.csv','Y':'crystals.csv', 'SW':'switches.csv'}

        key_comp = '' ; comp_class = ''
        desig_idx = -1
        for col in range(self.model.columnCount()):
            if str(self.model.data(self.model.index(0, col),
                    QtCore.Qt.DisplayRole )) == 'Designator':
                    desig_idx = col
            else:
                dic_param[str(self.model.data(self.model.index(0, col),
                    QtCore.Qt.DisplayRole ))] = col
        title = True
        for cur_row in range(self.model.rowCount()):
            if title:
                title = False
                continue
            prev_class = comp_class
            comp_class = ''
            for key in class_dico:
                if str(self.model.data(self.model.index(cur_row,desig_idx),
                        QtCore.Qt.DisplayRole)).startswith(key):
                    comp_class = class_dico[key]
            if comp_class == '':
                print('not complete')
                continue

##Voltage	Power	Tolerance	Temperature	ReverseVoltage	ForwardVoltage	Cont.Current	Frequency	ResonnanceFreq
            if comp_class != prev_class:
                first = True
                # create keyDico
                if comp_class == class_dico['C']:
                    # keyFormat is CAPA_VALUE_PACKAGE_VOLTAGE_TOLERANCE_TEMPERATURE
                    key_gen = ['Value','Package','Voltage','Tolerance','Temperature']
                elif comp_class == class_dico['D']:
#                    # keyFormat is DIOD_VALUE_PACKAGE_FORWARDVOLTAGE_REVERSEVOLTAGE_CONTINUOUSCURRENT
                    key_gen = ['Value','Package','ForwardVoltage','ReverseVoltage','Cont.Current']
                elif comp_class == class_dico['FB']:
                    #FIXME Here value is impedance at frequency.
                    # keyFormat is BEAD_VALUE_PACKAGE_FREQUENCY_CONTINUOUSCURRENT
                    key_gen = ['Value','Package','Frequency','Cont.Current']
                elif comp_class == class_dico['R']:
                    # keyFormat is RES_VALUE_PACKAGE_POWER_TOLERANCE
                    key_gen = ['Value','Package','Power','Tolerance']
                elif comp_class == class_dico['L']:
                    # keyFormat is INDU_VALUE_PACKAGE_CONT.CURRENT_RESONNANCEFREQ
                    key_gen = ['Value','Package','Cont.Current','ResonnanceFreq']
                elif comp_class == class_dico['U']:
                    # keyFormat is IC_VALUE_PACKAGE
                    key_gen = ['Value','Package']
                elif comp_class == class_dico['J'] or comp_class == class_dico['P']:
                    # keyFormat is CONN_VALUE_PACKAGE
                    key_gen = ['Value','Package']
                elif comp_class == class_dico['Y']:
                    # keyFormat is XTAL_VALUE_PACKAGE
                    #FIXME Chose if value is the frequency or the reference of the component
                    key_gen = ['Value','Package']
                elif comp_class == class_dico['SW']:
                    # keyFormat is BUTN_VALUE_PACKAGE
                    key_gen = ['Value']
                else:
                    continue

                # set filename according to class
                for key,value in class_dico.iteritems():
                    if value == comp_class:
                        file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),'db_files',class_files[key])

                key_gen_idx = {}
                db_param_list = {}
                # create dico of parameters necessary to create key
                for col in range(self.model.columnCount()):
                    for i in range(len(key_gen)):
                        if str(self.model.data(self.model.index(0, col),
                            QtCore.Qt.DisplayRole )) == key_gen[i]:
                                key_gen_idx[str(i)] = col
                                # set background to green to show that a value is expected in this cell
                                if str(self.model.data(self.model.index(cur_row, col),QtCore.Qt.DisplayRole)) == '_':
                                    color = QtCore.Qt.red
                                else:
                                    color = QtCore.Qt.darkGreen
                                self.model.setData(
                                    self.model.index(cur_row, col),
                                    QtGui.QColor(color),
                                    QtCore.Qt.BackgroundColorRole
                                    )
                                self.model.setData(
                                    self.model.index(cur_row, col),
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
                for k in key_gen_idx:
                    if str(self.model.data(self.model.index(cur_row, key_gen_idx[k]),QtCore.Qt.DisplayRole)) == '_':
                        color = QtCore.Qt.red
                    else:
                        color = QtCore.Qt.darkGreen
                    self.model.setData(
                        self.model.index(cur_row, key_gen_idx[k]),
                        QtGui.QColor(color),
                        QtCore.Qt.BackgroundColorRole
                        )
                    self.model.setData(
                        self.model.index(cur_row, key_gen_idx[k]),
                        QtGui.QColor(QtCore.Qt.white),
                        QtCore.Qt.TextColorRole
                        )

            if len(key_gen) > len(key_gen_idx):
                print('Missing parameters in you sch file')
                continue
            if not (file_name !='' and os.path.isfile(file_name)):
                continue
            key_comp = comp_class
#            key_fail = False
            # create key
            for i in range(len(key_gen_idx)):
                temp = str(self.model.data(self.model.index(cur_row,\
                           key_gen_idx[str(i)]),QtCore.Qt.DisplayRole))
#                if temp != '_' and temp != '':
                key_comp += '_' + str(self.model.data(self.model.index(cur_row,\
                                         key_gen_idx[str(i)]),QtCore.Qt.DisplayRole))
#                else:
#                    key_fail = True
#            if key_fail == True:
#                continue
            #print('new dbKey is :' + key_comp)
            # openfile
            with open(file_name, "rb") as fileInput:
            # create dbParamlist from first row
                first = True
                for row in csv.reader(fileInput):
                    if first:
                        for j in range(len(row)):
                            if row[j] != '' and row[j] != 'KEY':
                                db_param_list[row[j]] = j
                        first = False
                        #print(db_param_list)
                    else:
                        if row[0]==key_comp:
                            #update table
                            for key in db_param_list:
                                try:
                                    self.model.setData(self.model.index(cur_row,dic_param[key]),row[int(db_param_list[key])])
                                except:
                                    pass

    ###############################
    ## File Management Functions ##
    ###############################

    def load(self):
        path = os.getcwd()
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file',os.path.dirname(self.file_name), "*.csv *.sch")
        print(fname)
        if fname.lower().endswith('sch'):
            self.load_sch(fname)
        else:
            self.load_csv(fname)

    def load_csv(self, file_name):
        if file_name !='' and os.path.isfile(file_name):
            self.model.removeRows(0, int(self.model.rowCount()))
            with open(file_name, "rb") as fileInput:
                print('loading csv')
                for row in csv.reader(fileInput):
                    items = [
                        QtGui.QStandardItem(field)
                        for field in row
                    ]
                    self.model.appendRow(items)

    def load_sch(self,fname):
        if not (os.path.isfile(fname) and fname.endswith('.sch')):
            sys.exit(0)
        dictComponent = {'0':'Designator',
                         '1':'Value',
                         '2':'Footprint',
                         '3':'Datasheet',
                        }
        self.add_comp_to_table(fname,dictComponent)

    def add_comp_to_table(self, filename, dictComponent,first_row=True):
        column_order = {}
        sch = Schematic(filename)
        first = True
        for comp in sch.components:
            if '#PWR' in comp.labels['ref']:
                continue
            if first:
                i = 1
                comp_row0 = []
                comp_row0.append(QtGui.QStandardItem('ID'))
                column_order['ID'] = 0
                for field in comp.fields:
                    if field['name'] == '':
                        comp_row0.append(QtGui.QStandardItem(dictComponent[field['id']]))
                        column_order[field['id']] = i
                    else:
                        comp_row0.append(QtGui.QStandardItem(field['name'][1:-1]))
                        column_order[field['name'][1:-1]] = i
                    i+=1
                if first_row:
                    self.model.appendRow(comp_row0)
                    first_row = False
                first = False

            comp_row = []
            for i in range(len(comp_row0)):
                comp_row.append('_')
            comp_row[0] = comp.unit['time_stamp']
            for field in comp.fields:
                if field['name'] == '':
                    comp_row[column_order[field['id']]] = field['ref'][1:-1]
                elif field['name'][1:-1] == '':
                    continue
                else:
                    try:
                        comp_row[column_order[field['name'][1:-1]]] = field['ref'][1:-1]
                    except KeyError:
                        pass
            self.model.appendRow([ QtGui.QStandardItem(x) for x in comp_row])

        for sh in sch.sheets:
            for field in sh.fields:
                if field['id'] == 'F1':
                    if field['value'].find('.sch')!= -1:
                        sheetname = field['value'][1:-1]
            sheetname = os.path.join(os.path.dirname(filename),sheetname)
            self.add_comp_to_table(sheetname,dictComponent,False)

    def save_sch(self,fname):
        sch = Schematic(fname)
        for sh in sch.sheets:
            for field in sh.fields:
                # Find sheetname
                if field['id'] == 'F1':
                    if field['value'].find('.sch')!= -1:
                        sheetname = field['value'][1:-1]
                        sheetname = os.path.join(os.path.dirname(fname),sheetname)
                        # update the sheet sch file
                        self.save_sch(sheetname)
        for row in range(self.model.rowCount()):
            for comp in sch.components:
                if not str(comp.unit['time_stamp']) == str(self.model.data(self.model.index(row,0),
                QtCore.Qt.DisplayRole)):
                    continue
                for col in range(self.model.columnCount()):
                    for field in comp.fields:
                        compare_field = ''
                        if field['name'] != '':
                            compare_field = field['name'][1:-1]
                        if self.model.data(self.model.index(0,col),QtCore.Qt.DisplayRole) == compare_field:
#FIXME
#Update only if necessary: Worth it ?
#                            if field['ref'] != '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"':
                            if self.model.data(self.model.index(0,col),QtCore.Qt.DisplayRole) == None:
                                self.model.setData(self.model.index(row,col),'_')
                            field['ref'] = '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"'
                        elif col<= 4:
                            if field['id'] == str(col-1):
#                                if field['ref'] != '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"':
                                field['ref'] = '"' + self.model.data(self.model.index(row,col),QtCore.Qt.DisplayRole) + '"'
        sch.save()

    @QtCore.pyqtSlot()
    def save_sch_slot(self):
        print('SCH Saved')
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Update SCH file', os.path.dirname(self.file_name), "*sch")
        if not os.path.isfile(fname):
            print('ERROR Schematic file not found')
            return
        self.save_sch(fname)

    @QtCore.pyqtSlot()
    def save_csv_slot(self):
        path = os.path.dirname(self.file_name)
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save BOM', path, "*.csv")
        print(fname)
        if fname != '':
            self.save_BOM(fname)

    def write_BOM_row(self,item_line_num,qty,designators,row_number,col_number,writer):
      fields=[]
      fields.append(item_line_num)
      fields.append(qty)
      strfield='"'
      designators.sort(key=lambda x:map(safeint, re.findall("\d+|\D+", x)))
      for des in designators:
          if strfield != '"':
              strfield += ';'
          strfield += des
      strfield += '"'
      fields.append(strfield)
      for col_number in [2,5,6,7,9,10,8,11,12]:
          a = str(self.model.data(self.model.index(row_number-1, col_number),
              QtCore.Qt.DisplayRole ))
          if len(a)>0:
              if col_number != 0:
                  if a[0]!='"':
                      a = '"' + str(a) + '"'
              fields.append(a)
          else:
              a = '""'
              fields.append(a)
      writer.writerow(fields)
      designators = []
      designators.append(str(self.model.data(self.model.index(row_number, 1),
          QtCore.Qt.DisplayRole )))
      qty = 1
      item_line_num += 1
      return [item_line_num,qty,designators]

    def save_BOM(self, file_name):
        #first let's sort table by designator
        self.onSectionClicked(1)
        designators = []
        rowRem = []
        for row_number in range(self.model.rowCount()):
            des = str(self.model.data(self.model.index(row_number, 1),
                QtCore.Qt.DisplayRole ))
            if des not in designators:
                designators.append(des)
            else:
                rowRem.append(row_number)
                continue
        rowRem = sorted(rowRem,reverse=True)
        # remove duplicates
        for i in rowRem:
            self.model.removeRow(i)
        # set order to have same output whatever we sorted upon before
        self.sort_order = 0
        # sort by MFP
        self.onSectionClicked(6)

        print('filename=' + file_name)
        qty=1; first=1; prev_MFP = None; MFP=None; designators=[]
        prev_desig=None; desig=None
        strfield='"'
        item_line_num = 1
        with open(file_name, "wb") as file_output:
            writer = csv.writer(file_output,delimiter=',',quotechar="'")
            #initialize designators and MFP
            MFP = str(self.model.data(self.model.index(1, 6),
                        QtCore.Qt.DisplayRole ))
            designators.append(str(self.model.data(self.model.index(1, 1),
                        QtCore.Qt.DisplayRole )))
            fields = []
            fields.append('Line item #')
            fields.append('Qty')
            # export the title row as is
            for col_number in [1,2,5,6,7,9,10,8,11,12]:
                a = str(self.model.data(self.model.index(0, col_number),
                    QtCore.Qt.DisplayRole ))
                if len(a)>0:
                    if col_number != 0:
                        if a[0]!='"':
                            a = '"' + str(a) + '"'
                    fields.append(a)
                else:
                    a = '""'
                    fields.append(a)
            writer.writerow(fields)
            # now that header is ok lets browse the components
            # count the components having the same MFP
            for row_number in range(2,self.model.rowCount()+2):
                prev_MFP = MFP
                MFP = str(self.model.data(self.model.index(row_number, 6),
                    QtCore.Qt.DisplayRole ))
                if MFP == "DNP":
                  desig = str(self.model.data(self.model.index(row_number, 1),
                      QtCore.Qt.DisplayRole ))
                  if prev_MFP != "DNP":
                    [item_line_num,qty,designators] = self.write_BOM_row(item_line_num,qty,designators,row_number,col_number,writer)
                  else:
                    if prev_desig != None:
                      if desig.startswith(prev_desig):
                        qty += 1
                        designators.append(desig)
                      else:
                        [item_line_num,qty,designators] = self.write_BOM_row(item_line_num,qty,designators,row_number,col_number,writer)
                        match = re.search("\d", desig)
                        prev_desig = desig[:match.start()]
                    else:
                      match = re.search("\d", desig)
                      prev_desig = desig[:match.start()]
                      designators.append(str(self.model.data(self.model.index(row_number, 1),
                            QtCore.Qt.DisplayRole )))
                      qty = 1
                else:
                  if MFP == prev_MFP:
                    qty += 1
                    designators.append(str(self.model.data(self.model.index(row_number, 1),
                        QtCore.Qt.DisplayRole )))
                  else:
                    [item_line_num,qty,designators] = self.write_BOM_row(item_line_num,qty,designators,row_number,col_number,writer)

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
