kicad_reference_designs
=======================

This is a set of basic designs with the form of Kicad sheets that you can import in any project.

How to use it
=============

Open your current project
Create a sheet with the name of the module you want to use (e.g. FX3.sch).
then copy the file FX3.sch from osrf_hw/kicad_reference_designs/MCU/ to your project location.
Relaunch kicad and when you apen the sheet everything should have been imported properly.

NOTE1: do note create the sheet in your project after copying the file, this would cause KiCAD to segfault
NOTE2: the sch file lists the library it needs for the given design. You have to make sure to add those libraries to your project otherwise KiCAD won't recognize the symbols
