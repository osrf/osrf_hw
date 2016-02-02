from __future__ import print_function
import sys
sys.path.append('/usr/lib/freecad/lib')
print(sys.path)
import FreeCAD# as App
import ImportGui
import FreeCADGui# as Gui
import os
import Draft#,Sketch,Part
# lets assume for now that we have all the information in a filename
# lets also assume that they are only full ball arrays no missing ball in the center)
# all distances in mm
#TODO Argument passing
#FIXME doesnt handle different x and y pitch
#FIXME size of balls
#TODO Handle nissing balls according to pin quantity: or remove them by hand because impossible to handle all the fishy cases ?

#parameter = "/home/mikael/work/kicad_ws/osrf_hw_nonfree/BGAScriptTest/BGA900C80P30X30_2500X2500X150.wrl"
#parameter = "/home/mikael/work/kicad_ws/osrf_hw_nonfree/BGAScriptTest/BGA10C80P5X2_500X500X150.wrl"
parameter = sys.argv[2]
string = os.path.basename(parameter)
string = string[:string.rfind('.')]
directory = os.path.dirname(parameter)
idx = string.find('P')
pitch = float(string[string.find('C')+1:idx])/100.0
#print(pitch)
str2 = string[idx + 1 :] 
idx = str2.find('X')
nBallx = int(str2[:idx])
#print(nBallx)
str2 = str2[idx+1:]
idx = str2.find('_')
nBally = int(str2[:idx])
#print(nBally)
str2 = str2[idx+1:]
idx = str2.find('X')
length = float(str2[:idx])/100.0
#print(length)
str2 = str2[idx+1:]
idx = str2.find('X')
width = float(str2[:idx])/100.0
#print(width)
str2 = str2[idx+1:]
#idx = str2.find('.')
#height = float(str2[:idx])/100.0
height = float(str2)/100.0
#print(height)
ballradius = 0.225

# go in sketch mode
Gui.activateWorkbench("SketcherWorkbench")
# create doc
App.newDocument()
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")
print("document created")
# create sketch
App.activeDocument().addObject('Sketcher::SketchObject','Sketch')
print("sketch added")
App.activeDocument().Sketch.Placement = App.Placement(App.Vector(0.000000,0.000000,0.000000),App.Rotation(0.000000,0.000000,0.000000,1.000000))
Gui.activeDocument().setEdit('Sketch')
print("edit sketch")

# trace rectangle
App.ActiveDocument.Sketch.addGeometry(Part.Line(App.Vector(width/2.0,-length/2.0,0),App.Vector(-width/2.0,-length/2.0,0)))
App.ActiveDocument.Sketch.addGeometry(Part.Line(App.Vector(-width/2.0,-length/2.0,0),App.Vector(-width/2.0,length/2.0,0)))
App.ActiveDocument.Sketch.addGeometry(Part.Line(App.Vector(-width/2.0,length/2.0,0),App.Vector(width/2.0,length/2.0,0)))
App.ActiveDocument.Sketch.addGeometry(Part.Line(App.Vector(width/2.0,length/2.0,0),App.Vector(width/2.0,-length/2.0,0)))
print("place lines")
# add circular cutout
App.ActiveDocument.Sketch.addGeometry(Part.Circle(App.Vector(-width/2.0+1,length/2.0-1,0),App.Vector(0,0,1),0.5))


App.ActiveDocument.recompute()

Gui.getDocument('Unnamed').resetEdit()
App.getDocument('Unnamed').recompute()

# create pad from sketch
Gui.activateWorkbench("PartDesignWorkbench")
App.activeDocument().addObject("PartDesign::Pad","Pad")
App.activeDocument().Pad.Sketch = App.activeDocument().Sketch
App.activeDocument().Pad.Length = height
App.ActiveDocument.recompute()
Gui.activeDocument().hide("Sketch")
# change pad color to black
Gui.getDocument("Unnamed").getObject("Pad").ShapeColor = (0.00,0.00,0.00)
Gui.getDocument("Unnamed").getObject("Pad").Visibility=False #Hide pad

# Add Cylinder
Gui.activateWorkbench("PartWorkbench")
App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
FreeCAD.getDocument("Unnamed").getObject("Cylinder").Radius = 0.5
FreeCAD.getDocument("Unnamed").getObject("Cylinder").Height = height
FreeCAD.getDocument("Unnamed").getObject("Cylinder").Placement = App.Placement(App.Vector(-width/2.0+1,length/2.0-1,ballradius),App.Rotation(0,0,0,1))
App.ActiveDocument.recompute()


# Ball creation
App.ActiveDocument.addObject("Part::Sphere","Sphere")
App.ActiveDocument.recompute()
FreeCAD.getDocument("Unnamed").getObject("Sphere").Radius = ballradius
App.ActiveDocument.recompute()

# Ball Array creation
Gui.activateWorkbench("ArchWorkbench")
Draft.array(App.getDocument("Unnamed").getObject("Sphere"),App.Vector(pitch,0,0),App.Vector(0,pitch,0),nBallx,nBally)

## Merge all the spheres into a single object
Gui.activateWorkbench("PartWorkbench")
shapesToFuse=[]
for obj in FreeCAD.ActiveDocument.Objects:
  if obj.Name.find("Sphere") != -1:
    Gui.Selection.addSelection(obj)
    shapesToFuse.append(obj)
App.activeDocument().addObject("Part::MultiFuse","Fusion")
App.activeDocument().Fusion.Shapes = shapesToFuse
App.ActiveDocument.recompute()

fuse = FreeCAD.ActiveDocument.getObject("Fusion")
fuse.Placement = App.Placement(App.Vector(-(nBallx-1)*pitch/2.0,-(nBally-1)*pitch/2.0,ballradius),App.Rotation(0,0,0,1))
App.ActiveDocument.getObject("Pad").Placement = App.Placement(App.Vector(0,0,ballradius),App.Rotation(0,0,0,1))
Gui.ActiveDocument.getObject("Pad").Visibility=True
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewBottom()

## Export as a step model
expObjects = []
for obj in FreeCAD.ActiveDocument.Objects:
  # select all but indivudial Spheres and Sketch
  if (obj.Name.find("Sphere") == -1) and (obj.Name.find("Sketch") == -1):
    Gui.Selection.addSelection(obj)
    expObjects.append(obj)
  else:
    FreeCAD.ActiveDocument.removeObject(obj.Name)
#ImportGui.export(expObjects,os.path.join(directory,string+'.step'))

App.activeDocument().addObject("Part::MultiFuse","Fusion2")
App.activeDocument().Fusion2.Shapes = expObjects
App.ActiveDocument.recompute()
for obj in expObjects:
    FreeCAD.ActiveDocument.removeObject(obj.Name) 
expObjects= []

for obj in FreeCAD.ActiveDocument.Objects:
  if (obj.Name.find("Fusion2") != -1):
    expObjects.append(obj)
ImportGui.export(expObjects,os.path.join(directory,string+'.step'))
del expObjects
# Scale to inches before export to VRML for KiCAD use
Draft.scale(FreeCAD.ActiveDocument.ActiveObject, FreeCAD.Vector(0.3937,0.3937,0.3937))
FreeCAD.ActiveDocument.removeObject("Fusion2") 

### Export as a VRML model
expObjects = []
expObjects.append(FreeCAD.ActiveDocument.getObject("Scale"))
FreeCADGui.export(expObjects,os.path.join(directory,string+'.wrl'))
del expObjects
exit(1)
