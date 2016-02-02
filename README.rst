README.rst
==========

This repository contains the kicad module and libraries used at Open Source Robotics Foundation for the design of electronics boards.

Important note: All the scripts in this repository are under development and modified according to the immediate need of some projects. They are highly unstable and don't come with any warranty whatsoever.

Structure of this repository:
 * kicad_libraries: set of SchLib (components symbols) files either generated from scripts or created manually. Most of them should comply the KLC. Important note: these libraries have a lot more parameters than the standard KiCAD libraries to simplify the use of the scripts in the kicad_scripts folder
 * kicad_modules: set of kicad_mod files (footprints) either generated or created by hand. Most of them should comply with DLC. If not it's most likely to simplify the export to freeCAD in the future
 * kicad_reference_designs: A set of KiCAD sheets with standard configuration of a bunch of components (basic connection and related decoupling passives)
 * kicad_scripts: set of scripts to generate either SchLib/kicad_mod/wrl/step files for board design

Each folder will be provided with it's own README giving more detail about the content and how to use it
