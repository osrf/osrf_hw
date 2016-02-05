kicad_plugins
=============

This is the counterpart of the kicad_scripts folder. These plugins are made to be integrated in kicad and allows people who prefer GUI to scripting to have footprint wizards for a wider range of standard packages

Install
-------
pcbnew plugins
**************
To add these plugin to your kicad software, just copy paste the scripts to:
/usr/share/kicad/scripting/plugins
Then relaunch kicad and they should show up in the footprint wizard (open the footprint editor, open the footprint wizard, select wizard: first icon)

qfn_wizard.py
-------------
Allows you to create QFN packages footprints, it's basically the same plugin as QFP except that it adds an exposed pad in the center, you can adjust the epad dimension using the "epad width" and "epad length" parameters
Future work
***********
Make a generic plugin that QFP and QFN will inherit from and store everything in one file. This would limit code duplication

sdip_wizard.py
--------------
script registering 3 plugins: one for SOIC/SOP/SSOP/TSOP etc, one for SIP/DIP and one for SON.
The SON one adds an exposed pad in the center of the package, you can adjust it's size using the "epad width" and "epad length" parameters
