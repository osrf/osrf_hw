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
#FIXME doesnt handle different x and y pitch
#FIXME size of balls
# remove them by hand because impossible to handle all the fishy cases ?
MMTOMIL = 0.3937

directory = sys.argv[2]; name = sys.argv[3]; pitch = float(sys.argv[4])
nBallx = int(sys.argv[5]); nBally = int(sys.argv[6])
length = float(sys.argv[7]); width = float(sys.argv[8])
height = float(sys.argv[9]); ballradius = pitch/4.

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
App.activeDocument().Sketch.Placement = App.Placement(App.Vector(0.0,0.0,0.0),App.Rotation(0.0,0.0,0.0,1.0))
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
exp_objects = []
for obj in FreeCAD.ActiveDocument.Objects:
  # select all but indivudial Spheres and Sketch
  if (obj.Name.find("Sphere") == -1) and (obj.Name.find("Sketch") == -1):
    Gui.Selection.addSelection(obj)
    exp_objects.append(obj)
  else:
    FreeCAD.ActiveDocument.removeObject(obj.Name)

App.activeDocument().addObject("Part::MultiFuse","Fusion2")
App.activeDocument().Fusion2.Shapes = exp_objects
App.ActiveDocument.recompute()
for obj in exp_objects:
    FreeCAD.ActiveDocument.removeObject(obj.Name) 
exp_objects= []

exp_objects.append(FreeCAD.ActiveDocument.getObject("Fusion2"))
ImportGui.export(exp_objects,os.path.join(directory, name + '.step'))
del exp_objects
# Scale to mil before export to VRML for KiCAD use
Draft.scale(FreeCAD.ActiveDocument.ActiveObject, FreeCAD.Vector(MMTOMIL,MMTOMIL,MMTOMIL))
FreeCAD.ActiveDocument.removeObject("Fusion2") 

### Export as a VRML model
exp_objects = []
exp_objects.append(FreeCAD.ActiveDocument.getObject("Scale"))
FreeCADGui.export(exp_objects,os.path.join(directory, name + '.wrl'))
del exp_objects
exit(1)
