Before you use the batch exporter ensure the following;

1. All source (.max, .mb) files and all destination (.visual, .primitive, .model, .animation) files are backed up with source control.
2. 3d Studio Max and Maya are installed.
3. Both 3dsMax and Maya executable paths are entered in the System Environment Variables.
3. The BigWorld Maxscripts installed using bigworld_maxscripts_v1.8.mzp or later. The maxscript installer can be found in "bigworld\tools\maxscripts\" and instructions on how to install them, found in the content_creation.chm
4. The userSetup.mel script containing the bigworld_batch_exporter procedure should be been placed into "Documents and Settings\User\My Documents\maya\versionNumber\scripts". If you have an existing userSetup.mel script you can simply append the contents of the above file to the existing file. 
5. BigWorld exporters installed and paths.xml set up correctly. 
6. Reboot your system at least once after 3dsMax and Maya installation to ensure environment variables are registered.

What the batch exporter does;
1. Searches through all sub folders of the Source directory and creates a list of all ".max" (3d Studio Max), ".mb" (Maya Binary) and ".ma" (MayaASCII) files.
2. Duplicates the hierarchy of the Source directory at the destination directory if the folders don't already exist. 
3. Launches 3dsMax from the command line and passes it the list of .max files to be exported using a function in 3dsMax's startup script. 
4. Assets with "animation" in their file path will be exported as .animation files otherwise a .visual export is performed.
4. Launches Maya from the command line and passes it the list of .mb files to be exported using a procedure in Maya's userSetup.mel startup script. 
5. Writes all exported files to a log file created in the Source folder. 
