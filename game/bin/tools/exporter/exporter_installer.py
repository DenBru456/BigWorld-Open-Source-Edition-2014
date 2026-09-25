# This script installs 3dsmax and Maya exporter and the toolbar/shelf
#
# Usage:
# python exporter_installer.py -s [game parent directory] -v [Maya/3DMax version]


import optparse
import sys
import os
import shutil
import stat

try:
	import win32com.client
except ImportError:
	print "ERROR: win32com is needed for this script"
	print "download win32com, for your python version-"
	print "http://sourceforge.net/projects/pywin32/files/pywin32/"
	sys.exit(1)

from distutils import dir_util

MAYA_DIR = { 	"maya2014x64":"2014-x64",
				"maya2013x64":"2013-x64",
				"maya2013":"2013",
				"maya2012x64":"2012-x64",
				"maya2012":"2012",
				"maya2011x64":"2011-x64",
				"maya2011":"2011",
				"maya2010x64":"2010-x64",
				"maya2010":"2010"
			}

MAX_DIR = {		"3dsmax2013x64":"ADSK_3DSMAX_x64_2013",
				"3dsmax2013":"ADSK_3DSMAX_x86_2013",
				"3dsmax2012x64":"ADSK_3DSMAX_x64_2012",
				"3dsmax2012":"ADSK_3DSMAX_x32_2012",
				"3dsmax2011x64":"3DSMAX_2011x64_PATH",
				"3dsmax2011":"3DSMAX_2011_PATH"
			}
			
EXECUTABLES = MAYA_DIR.keys() + MAX_DIR.keys()

def copyFilesWithExtension ( srcDir, dstDir, extension ):
	for root, dirs, files in os.walk(srcDir):
			for file_ in files:
				if file_.endswith(extension):
					forceCopy(os.path.join(root, file_), os.path.join(dstDir, file_))

def forceCopy( originalFile, destFile ):
	if os.path.exists( destFile ):
		if os.access(destFile, os.F_OK) and not os.access(destFile, os.W_OK):
			os.chmod(destFile, stat.S_IWUSR)
	elif not os.path.exists( os.path.dirname(destFile) ):
		os.makedirs(os.path.dirname(destFile))
	shutil.copy( originalFile, destFile )
	os.chmod(destFile, stat.S_IWUSR)

def setMayaEnv( sourceName, destName, mayaVersion ):

	GAME_DIR = EXPORTER_FOLDER = os.path.join( sourceName, "game")
	BIGWORLD_RES_DIR = os.path.join( GAME_DIR, "res", "bigworld")
	GAME_TOOLS = os.path.join( GAME_DIR, "bin", "tools")
	BIGWORLD_MELSCRIPT =  os.path.join( GAME_TOOLS, "melscripts")
	EXPORTER_FOLDER = os.path.join( GAME_TOOLS, "exporter")
	RES_FOLDER =  os.path.join( GAME_DIR, "res", "fantasydemo")
	MAYA_ENV_FILE = "Maya.env"
	SHELF_FILE = os.path.join( BIGWORLD_MELSCRIPT, 
								"src", "shelf", "shelf_BigWorld.mel" ) 
	
	#set maya documents folder
	documents_folder = os.path.join( destName, "maya\\" + MAYA_DIR[mayaVersion] ) 
	
	
	#set maya.env file
	MAYA_PLUG_IN_DIR = os.path.join( EXPORTER_FOLDER, "mayaPlugin")
	MAYA_PLUG_IN_PATH = os.path.join( EXPORTER_FOLDER, mayaVersion)
	MAYA_PLUG_IN_PATH = MAYA_PLUG_IN_PATH.replace("\\","/")
	mayaEnv_file = os.path.join( documents_folder, MAYA_ENV_FILE ) 
	
	f_tmp = open( mayaEnv_file+"_co", "wt" )
	f_tmp.write( "MAYA_PLUG_IN_PATH = "+MAYA_PLUG_IN_PATH+"\n" )
	f_tmp.write( "BATCH_EXPORTER_TEST = "+RES_FOLDER.replace("\\","/")+"\n" )
	f_tmp.write( "BIGWORLD_RES_DIR = "+BIGWORLD_RES_DIR.replace("\\","/")+"\n" )	
	f_tmp.write( "MAYA_DISABLE_CIP=1" )
	
	if os.path.exists( mayaEnv_file):
		f_org = open( mayaEnv_file, "r" )
		#copy lines which are already exist
		for line in f_org:
			if ( not "BATCH_EXPORTER_TEST" in line ) and \
				 ( not "MAYA_DISABLE_CIP" in line ) and\
				 ( not "MAYA_PLUG_IN_PATH" in line ) and\
				 ( not "BIGWORLD_RES_DIR" in line ):
				f_tmp.write( "\n"+line )
		
		f_org.close()
	f_tmp.close()
	
	forceCopy( mayaEnv_file+"_co", mayaEnv_file )
	os.remove( mayaEnv_file+"_co" )
	
	print "Set maya.env file:"
	print "MAYA_DISABLE_CIP=1"
	print "MAYA_PLUG_IN_PATH = "+MAYA_PLUG_IN_PATH
	print "BATCH_EXPORTER_TEST = "+RES_FOLDER +"\n"
	
	#MAYA SHELF INSTALLATION
	#copy the shelf_BigWorld.mel file
	new_file_loc = os.path.join( documents_folder, 
								"prefs\\shelves\\shelf_BigWorld.mel" )
	forceCopy( SHELF_FILE, new_file_loc )
	
	print "copy shelf_BigWorld.mel file to " + new_file_loc + "\n"
	
	#BigWorld's shelf icons the Maya icons folder
	org_file_loc = os.path.join( BIGWORLD_MELSCRIPT, "src\\icons" )
	new_file_loc = os.path.join( documents_folder, "prefs\\icons" )
	copyFilesWithExtension ( org_file_loc, new_file_loc, "bmp" )
	copyFilesWithExtension ( org_file_loc, new_file_loc, "png" )
	
	print "copy shelf icons to " + new_file_loc + "\n"
	
	#Copy BigWorld's Maya Python scripts to the Maya shelves folder
	org_file_loc = os.path.join( BIGWORLD_MELSCRIPT, "src\\scripts" )
	new_file_loc = os.path.join( documents_folder, "prefs\\scripts" )
	copyFilesWithExtension ( org_file_loc, new_file_loc, "py" )
	
	print "Copy BigWorld's Maya Python scripts to " + new_file_loc + "\n"
	
	#copy userSetup.mel
	org_file_loc = os.path.join( MAYA_PLUG_IN_DIR, "userSetup.mel" )
	new_file_loc = os.path.join( documents_folder, "scripts\\userSetup.mel" )
	forceCopy( org_file_loc, new_file_loc )
	
	print "Copy userSetup.mel file to " + new_file_loc + "\n"
	
	#copy paths.xml and visualfileexporterscript.mel to the version plugin dir
	org_file_loc = os.path.join( MAYA_PLUG_IN_DIR, "paths.xml" )
	new_file_loc = os.path.join( MAYA_PLUG_IN_PATH, "paths.xml" )
	forceCopy( org_file_loc, new_file_loc )
	org_file_loc = os.path.join( MAYA_PLUG_IN_DIR, "visualfileexporterscript.mel" )
	new_file_loc = os.path.join( MAYA_PLUG_IN_PATH, "visualfileexporterscript.mel" )
	forceCopy( org_file_loc, new_file_loc )
	
	print "Copy userSetup.mel file to " + new_file_loc + "\n"
	
def setMaxEnv( sourceName, maxVersion ):

	bigWorldDir = os.path.join(sourceName, "game" )
	
	if "x64" in maxVersion:
		versionDirName = maxVersion.split('x')[1] + " - 64bit"
	else:
		versionDirName = maxVersion.split('x')[1] + " - 32bit"
		
	autodeskDir = os.path.join(os.getenv('APPDATA'), "..", "Local", "Autodesk", "3dsMax", \
								versionDirName, "enu", "scripts" )

	org_file_loc = os.path.join( bigWorldDir, "bin", "tools", "maxscripts", "src", "BigWorld_MAXScripts",\
								"BigWorld_Common.ms" )
	new_file_loc = os.path.join( autodeskDir, "BigWorld_Common.ms" )
	print "Copy BigWorld_Common.ms file to " + new_file_loc + "\n"
	forceCopy( org_file_loc, new_file_loc )
	
	org_file_loc = os.path.join( bigWorldDir, "bin", "tools", "maxscripts", "src", "BigWorld_StartupScripts",\
								"BigWorld_Startup.ms" )
	new_file_loc = os.path.join( autodeskDir, "startup", "BigWorld_Startup.ms" )
	print "Copy BigWorld_Startup.ms file to " + new_file_loc + "\n"
	forceCopy( org_file_loc, new_file_loc )
	
	bigWorldDir = bigWorldDir.replace( "\\", "\\\\" )
	
	basePath = os.environ[MAX_DIR[maxVersion]]
		
	maxCmdString = "3dsmax"	
	maxCmdOptions = " -mxs \"Set_BigWorld_Setting \\\"" + bigWorldDir + "\\\"\"" 
						
	varPathMaxCmdString = os.path.join( basePath, maxCmdString )
	varPathMaxCmdStringOptions = ("\"\"" + varPathMaxCmdString + "\" " \
									+ maxCmdOptions+ "\"")
	print "Updating BigWorld folder " + bigWorldDir + " in " + maxVersion + "\n"
	os.system( varPathMaxCmdStringOptions )
	
		
def setEnv():
	usage = "\npython %prog -s [game parent directory] " + \
			"-v [Maya/3DMax version]\n"
	
	parser = optparse.OptionParser( usage )
	
	parser.add_option( "-s", "--source",
			dest = "sourceName", default=None,
			help = "game parent directory\n" )

	parser.add_option( "-v", "--version",
			dest = "version", default=None,
			help = "version:\n" + "|".join( EXECUTABLES )+"\n")		
						
	(options, args) = parser.parse_args() 
	
	if None == options.sourceName:
		print "\nPlease specify the Current directory\n"
		parser.print_help()
		return 1
			
	if None == options.version:
		print "\nPlease specify Maya/3DMax version\n"
		parser.print_help()
		return 1
			
	if not os.path.exists( options.sourceName ):
		print "\nCannot find "+ options.sourceName +"\n"
		parser.print_help()
		return 1
	if not os.path.exists( os.path.join(options.sourceName, "game") ):
		print "\ngame folder doesn't exist in source provided\n"
		parser.print_help()
		return 1
	
	if options.version in MAYA_DIR:
		oShell = win32com.client.Dispatch("Wscript.Shell")
		setMayaEnv( options.sourceName, oShell.SpecialFolders("MyDocuments"), options.version )
	elif options.version in MAX_DIR:
		setMaxEnv( options.sourceName, options.version )
	else:
		print "\n"+options.version + " is not a valid version\n"
		parser.print_help()
		return 1
	return 0


if __name__ == "__main__":
	sys.exit( setEnv() )