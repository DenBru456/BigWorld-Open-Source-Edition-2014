How to batch export all exporter test files. 

------------
PREPARATION:
------------
1. The /res folder "http://svn/svn/mf/projects/trunk/testworld/test3dsourcefiles/batchable_exporter_test_files/res" in the same directory as this readme should be set up as the project folder for the versions of 3dsMax and Maya that you are batch exporting. This will enable the relative paths used for bitmaps in each of the test source files

To set 3dsMax to use relatives paths:
Go to File-Manage-Set Project folder.
Customize - Preferences - Files - Convert file paths to UNC = True
Convert local file paths to Relative = True
3dsMax will dump a create a set of folders at this location, ignore them.

To set Maya to use relative paths:
File - Project - Set:
Edit the maya.env file (C:\Users\username\Documents\maya\2011\Maya.env) so that it contains the following environment variable, where the global path is the location of your export directory res folder e.g.
BATCH_EXPORTER_TEST = C:/mf_20_current/fantasydemo/res
Note: The Maya.env file should also contain the location of the BigWorld Exporter on a separate line e.g.
MAYA_PLUG_IN_PATH = C:/mf_20_current/bigworld/tools/exporter/maya2011


2. Each version of 3dsMax you are testing will require an install the BigWorld exporters using the BigWorld maxscript installer located here
bigworld\tools\maxscripts\bigworld_maxscripts_v1.8.mzp
This will also ensure that the appropriate paths are set up in 3dsMax's External Files.
The most important path will be the location of the BigWorld Shaders.
To check this, go to Customize - Configure User Paths - External Files
bigworld\res\shaders\std_effects

NOTE: When changing between different versions of BigWorld you can use the exporter_swap.py script located here (C:\mf_testworld\scripts\art\swap_exporter\exporter_swap.py) to quickly change all 
your versions of 3dsMax to the desired BigWorld version but be warned, the shader preview files used in the 3dsMax viewport will be from the BigWorld version that you ran the installer from. 
This is only important if you are testing the shader preview functionality inside 3dsMax and makes no difference to the exported file, so generally it can be ignored.
However, if you are testing shader viewport preview the correct shaders can be accessed by changing the URL in Customize - Configure User Paths - External Files - bigworld\res\shaders\std_effects

-------------------------
RUNNING THE BATCH EXPORT:
-------------------------
1. Run the batch exporter located here (bigworld\tools\batch_exporter\batch_exporter.py). You may require an install of python (2.6)

2. Choose Source directory
mf_testworld\test3dsourcefiles\batchable_exporter_test_files\res\exporter_test_files

3. Set the export directory to
\fantasydemo\res\exporter_test_files
This is important as it will ensure that the relative paths to the shaders are correct.

4. Select Copy bitmaps,
The bitmaps will be locally UNC referrenced within 3dsMax providing you have set the project folder correctly.

5. Select Copy .animationsettings and .visualsettings
The presence of a .visualsettings and/or .animationsettings will be used to determine what type (.visual or .animation) file is to be exported and to pre-set the options. 
This works only for 3dsMax as Maya does not create .visual settings and is not scriptable (yet)

6. Select desired 3dsMax and Maya versions (Note that all Maya exported files will require manual control over the exporter settings)
The script starts up 3dsMax by executing "3dsMax.exe" in the command prompt preceded by the system environment variable modifier below. The script will report a missing environment variable if it cannot find one.
MAX_SYSTEM_VARS = ("3DSMAX_2011_PATH", "3DSMAX_2011x64_PATH", "ADSK_3DSMAX_x32_2012", "ADSK_3DSMAX_x64_2012", "ADSK_3DSMAX_x86_2013",
                          "ADSK_3DSMAX_x64_2013", "ADSK_3DSMAX_x86_2014", "ADSK_3DSMAX_x64_2014")

7. Begin Export. 

8. The batch export script will duplicate the folder structure of the chosen source directory and copy any desirable files to the source directory. It will then export each file in turn. 

NOTE: Some exporter test cases cannot be automatically tested.
# Test_017_use_reference_hierarchy_2.max does not work automatically. It requires
a user to input the reference visual path http://bugs.bigworldtech.com/show_bug.cgi?id=32010
# Test case test_18_use_current_scene_state.max will not work as it requires a modification
to the max file before export
# Test_019_export_selected.max requires the user to select and export a specific group of objects
# Test_042_bsp_not_recreated will require a second export after scaling the model
# Test_045_edit_normals will require manual export as the edit normals modifier needs to be selected before
export
# Test_059b_incorrect_scale_direction_userefhierarchy.max does not work automatically. It requires
a user to input the reference visual path http://bugs.bigworldtech.com/show_bug.cgi?id=32010
# Test_076a_vertex_normal_seams AND test_076b_vertex_normal_seams will require a manual export to get a positive result.
Currently the exporter requires EDIT NORMAL modifiers to be selected on export if edited normals are to be exported.
The automatically exported version will be a negative test.

-----------------------------
When creating new test files:
-----------------------------
1. Ensure that any bitmap paths referenced within the materials of the test files are local referenced