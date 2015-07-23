# Set the directory variable before running

import FreeCAD
import ImportGui
import FreeCADGui
import os

directory = "/home/mikael/kicad_ws/osrf_hw/kicad_3dmodels/BGA"
if not os.path.isdir(directory):
    print "ERROR directory " + directory + " doesn't exist"
    exit(1)
for root, subdirs, files in os.walk(directory):
    for filename in files:
        if filename.lower().endswith('.stp') or filename.lower().endswith('.step'):
            file_path = os.path.join(root,filename)
            ImportGui.open(file_path)
            wrlname = file_path[0:file_path.rfind(file_path[file_path.rfind('.'):])] + ".wrl"
            Gui.export(App.ActiveDocument.findObjects("Part::Feature"),wrlname)
            App.closeDocument(App.ActiveDocument.Name)
exit(1)

