from __future__ import print_function
import sys
sys.path.append('/usr/lib/freecad/lib')
print(sys.path)
import FreeCAD
import ImportGui
import FreeCADGui
import os
import Draft
# FIXME assumes standoff of 0.5mm
# all distances in mm

MMTOMIL = 0.3937

directory = sys.argv[2]; name = sys.argv[3]; pitch = float(sys.argv[4])
nHorizontalPins = int(sys.argv[5]); nVerticalPins = int(sys.argv[6])
sizePinx = float(sys.argv[7]); sizePiny = float(sys.argv[8]); sizePinz = float(sys.argv[9]);
length = float(sys.argv[10]); width = float(sys.argv[11])
height = float(sys.argv[12])
mode = 'QFP'
if len(sys.argv) > 13:
  mode = 'QFN'
  sizeEpadx = float(sys.argv[13])
  sizeEpady = float(sys.argv[14])

# go in sketch mode
Gui.activateWorkbench("SketcherWorkbench")
# create doc
App.newDocument()
App.setActiveDocument("Unnamed")
App.ActiveDocument=App.getDocument("Unnamed")
Gui.ActiveDocument=Gui.getDocument("Unnamed")

# create sketch
App.activeDocument().addObject('Sketcher::SketchObject','Sketch')
App.activeDocument().Sketch.Placement = App.Placement(
    App.Vector(0.0, 0.0, 0.05),
    App.Rotation(0.0, 0.0, 0.0, 1.0))
Gui.activeDocument().setEdit('Sketch')

# trace rectangle
App.ActiveDocument.Sketch.addGeometry(Part.Line(
    App.Vector(width/2.0, -length/2.0, 0),
    App.Vector(-width/2.0, -length/2.0, 0)))
App.ActiveDocument.Sketch.addGeometry(Part.Line(
    App.Vector(-width/2.0, -length/2.0, 0),
    App.Vector(-width/2.0, length/2.0, 0)))
App.ActiveDocument.Sketch.addGeometry(Part.Line(
    App.Vector(-width/2.0, length/2.0, 0),
    App.Vector(width/2.0, length/2.0, 0)))
App.ActiveDocument.Sketch.addGeometry(Part.Line(
    App.Vector(width/2.0, length/2.0, 0),
    App.Vector(width/2.0, -length/2.0, 0)))

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
FreeCAD.getDocument("Unnamed").getObject("Cylinder").Radius = sizePinx/2.
FreeCAD.getDocument("Unnamed").getObject("Cylinder").Height = height
FreeCAD.getDocument("Unnamed").getObject("Cylinder").Placement = App.Placement(
    App.Vector(-width/2.0 + 2*sizePinx, length/2.0 - 1 + 2 * sizePinx, 0.1),
    App.Rotation(0,0,0,1))
App.ActiveDocument.recompute()

# Pin Creation
App.ActiveDocument.addObject("Part::Box","HorizontalPin")
App.ActiveDocument.recompute()
FreeCAD.getDocument("Unnamed").getObject("HorizontalPin").Length = sizePinx
FreeCAD.getDocument("Unnamed").getObject("HorizontalPin").Width = sizePiny
FreeCAD.getDocument("Unnamed").getObject("HorizontalPin").Height = sizePinz
App.ActiveDocument.recompute()

# Horizontal pin Array creation
Gui.activateWorkbench("ArchWorkbench")
Draft.array(
    App.getDocument("Unnamed").getObject("HorizontalPin"),
    App.Vector(pitch, 0, 0), App.Vector(0, width-sizePiny, 0), nHorizontalPins, 2)

Gui.activateWorkbench("PartWorkbench")
shapesToFuse=[]
for obj in FreeCAD.ActiveDocument.Objects:
  if obj.Name.find("HorizontalPin") != -1:
    Gui.Selection.addSelection(obj)
    shapesToFuse.append(obj)
App.activeDocument().addObject("Part::MultiFuse","HorizontalFusion")
App.activeDocument().HorizontalFusion.Shapes = shapesToFuse
App.ActiveDocument.recompute()

fuse = FreeCAD.ActiveDocument.getObject("HorizontalFusion")
fuse.Placement = App.Placement(
    App.Vector(-((nHorizontalPins-1) * pitch / 2.0 + sizePinx / 2.), -length / 2., 0),
    App.Rotation(0,0,0,1))

# Vertical pin Array creation
# Pin Creation
App.ActiveDocument.addObject("Part::Box","VerticalPin")
App.ActiveDocument.recompute()
FreeCAD.getDocument("Unnamed").getObject("VerticalPin").Length = sizePiny
FreeCAD.getDocument("Unnamed").getObject("VerticalPin").Width = sizePinx
FreeCAD.getDocument("Unnamed").getObject("VerticalPin").Height = sizePinz
App.ActiveDocument.recompute()
Draft.array(App.getDocument("Unnamed").getObject("VerticalPin"), 
    App.Vector(0, pitch, 0),
    App.Vector(length-sizePiny, 0, 0),
    nVerticalPins, 2)

Gui.activateWorkbench("PartWorkbench")
shapesToFuse=[]
for obj in FreeCAD.ActiveDocument.Objects:
  if obj.Name.find("VerticalPin") != -1:
    Gui.Selection.addSelection(obj)
    shapesToFuse.append(obj)
App.activeDocument().addObject("Part::MultiFuse","VerticalFusion")
App.activeDocument().VerticalFusion.Shapes = shapesToFuse
App.ActiveDocument.recompute()

fuse = FreeCAD.ActiveDocument.getObject("VerticalFusion")
fuse.Placement = App.Placement(
    App.Vector(-width / 2., -((nVerticalPins-1) * pitch / 2.0 + sizePinx / 2.), 0),
    App.Rotation(0,0,0,1))

if mode == 'QFN':
  # create the exposed pad
  App.ActiveDocument.addObject("Part::Box","EPAD")
  App.ActiveDocument.recompute()
  FreeCAD.getDocument("Unnamed").getObject("EPAD").Length = sizeEpadx
  FreeCAD.getDocument("Unnamed").getObject("EPAD").Width = sizeEpady
  FreeCAD.getDocument("Unnamed").getObject("EPAD").Height = sizePinz
  App.ActiveDocument.getObject("EPAD").Placement = App.Placement(
      App.Vector(-sizeEpadx/2., -sizeEpady/2., 0),
      App.Rotation(0, 0, 0, 1))
  App.ActiveDocument.recompute()

Gui.ActiveDocument.getObject("Pad").Visibility=True
 
## Export as a step model
exp_objects = []
for obj in FreeCAD.ActiveDocument.Objects:
  # select all but indivudial Spheres and Sketch
  if (obj.Name.find("Pin") == -1) and (obj.Name.find("Sketch") == -1):
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
Draft.scale(FreeCAD.ActiveDocument.ActiveObject,
    FreeCAD.Vector(MMTOMIL, MMTOMIL, MMTOMIL))
FreeCAD.ActiveDocument.removeObject("Fusion2") 

### Export as a VRML model
exp_objects = []
exp_objects.append(FreeCAD.ActiveDocument.getObject("Scale"))
FreeCADGui.export(exp_objects,os.path.join(directory, name + '.wrl'))
del exp_objects
exit(1)
