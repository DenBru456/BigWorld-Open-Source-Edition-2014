import glob
import optparse
import sys
import subprocess
import filecmp
import threading
from Tkinter import *
from tkFileDialog import askdirectory
from tkFileDialog import askopenfilename
import tkMessageBox
import os
import shutil
import time
from time import gmtime, strftime, localtime
from datetime import datetime
import reporter

try:
	import ImageGrab
except ImportError:
	print "ERROR: ImageGrab is needed for this script"
	print "download PIL 1.1.7, for your python version-"
	print "http://www.pythonware.com/products/pil/"
	sys.exit(1)
from PIL import Image

TIMEOUT = 60*15

g_lf = None #log file and full path

MAX_2011_32		= "3DSMAX_2011_PATH"
MAX_2011_64		= "3DSMAX_2011x64_PATH"
MAX_2012_32		= "ADSK_3DSMAX_x32_2012"
MAX_2012_64		= "ADSK_3DSMAX_x64_2012"
MAX_2013_32		= "ADSK_3DSMAX_x86_2013"
MAX_2013_64		= "ADSK_3DSMAX_x64_2013"

MAX_VISUAL_DIR = { "3DSMAX_2011_PATH":"2011_32_visual_files",
				"3DSMAX_2011x64_PATH":"2011_64_visual_files",
				"ADSK_3DSMAX_x32_2012":"2012_32_visual_files",
				"ADSK_3DSMAX_x64_2012":"2012_64_visual_files",
				"ADSK_3DSMAX_x86_2013":"2013_32_visual_files",
				"ADSK_3DSMAX_x64_2013":"2013_64_visual_files",
			}

MAX_EXECUTABLES = [ MAX_2011_32, MAX_2011_64, MAX_2012_32, MAX_2012_64,
		MAX_2013_32, MAX_2013_64 ]

MAYA_VISUAL_DIR = { "MAYA_2011_32":"2011_32_visual_files",
				"MAYA_2011_64":"2011_64_visual_files",
				"MAYA_2012_32":"2012_32_visual_files",
				"MAYA_2012_64":"2012_64_visual_files",
				"MAYA_2013_32":"2013_32_visual_files",
				"MAYA_2013_64":"2013_64_visual_files",
				"MAYA_2014_64":"2014_64_visual_files",
			}
			
MAYA_VERSION = [ "MAYA_2011_32", "MAYA_2011_64", "MAYA_2012_32", "MAYA_2012_64",
		"MAYA_2013_32", "MAYA_2013_64", "MAYA_2014_64" ]
		
MAX_VERSION = { "3DSMAX_2011_PATH":"3DSMAX_2011_32",
				"3DSMAX_2011x64_PATH":"3DSMAX_2011_64",
				"ADSK_3DSMAX_x32_2012":"3DSMAX_2012_32",
				"ADSK_3DSMAX_x64_2012":"3DSMAX_2012_64",
				"ADSK_3DSMAX_x86_2013":"3DSMAX_2013_32",
				"ADSK_3DSMAX_x64_2013":"3DSMAX_2013_64",
			}

MODEL_EDITOR_FILE = "modeleditor.exe"
MODEL_EDITOR_OPTIONS_FILE = "modeleditor.options"
MODEL_EDITOR_LAYOUT_FILE = "modeleditor.layout"
MODEL_EDITOR_PATH = "..\\modeleditor\\win64"
MODEL_EDITOR_RES_PATH = "..\\modeleditor\\resources"
MODEL_EDITOR_SCRIPTS_PATH = os.path.join(MODEL_EDITOR_RES_PATH, "scripts")

GRAPHICS_PREFERENCES_FILE = "graphics_preferences.xml"

VISUAL_EXT = ".visual"
TMP_FOLDER = "tmp"

MAX_DIR = "testmaxfiles"
MAYA_DIR = "testmayafiles"
DEBUG_LOG_FILE = "debug.log"
EXPORT_LOG_FILE = "export.txt"
IMAGE_COMPARE_LOG_FILE = "image_compare.log"
RESULTS_LOG_FILE = "results.log"
HTML_NAME = "screenshots.html"

additional_error_messages = ""

# Gets all directories and subdirectores of root
def recursiveDirGen( mydir ):
	for root, dirs, files in os.walk( mydir ):
		for dir in dirs:
			yield os.path.join( root, dir )

# Gets all files in directories and subdirectores of root
def recursiveFileGen( mydir ):
	for root, dirs, files in os.walk( mydir ):
		for file in files:
			yield os.path.join( root, file )

def createListOfExportFiles( logDir, fileName ): #logDir is root
	listOfExportFiles = os.path.join( logDir, fileName )
	return listOfExportFiles

def appendListFile ( data, list_file ): 
	#Append function for both max and maya list
	list_file.write( data )
	list_file.write( "\n" )

def deleteLogFile( logDir ): #logDir is root
	logFile_url = os.path.join (logDir, EXPORT_LOG_FILE)
	if os.path.exists( logFile_url ):
		os.remove( logFile_url )
	#re-create DEBUG_LOG_FILE
	tmp = open( DEBUG_LOG_FILE, 'w' )
	tmp.close()
	
def backUpLogFile( logDir, version ): #logDir is root
	if version in MAX_EXECUTABLES:
		version = MAX_VERSION[version]
	logFile_url = os.path.join (logDir, EXPORT_LOG_FILE)
	
	t = strftime( "%a_%d_%b_%Y_%H_%M_%S", localtime())
	updated_logFile_url = \
				os.path.join(logDir, t + "_" + version + "_" + EXPORT_LOG_FILE)
	
	if os.path.exists( logFile_url ):
		shutil.move( logFile_url, updated_logFile_url )
		print "Please see " + updated_logFile_url + " for summary\n\n"
	else:
		print "Export File haven't created\n\n"
	
	if os.path.exists( DEBUG_LOG_FILE ):
		updated_logFile_url = os.path.join(logDir, t + "_" + version + "_debug.log")
		shutil.move( DEBUG_LOG_FILE, updated_logFile_url )
			
def createLogFile( logDir, msg ): #logDir is root
	global g_lf
	logFile_url = os.path.join (logDir, EXPORT_LOG_FILE)
	g_lf = open( logFile_url, 'a' )
	g_lf.write( msg )
	t = strftime( "%a, %d %b %Y %H:%M:%S +0000", localtime())            
	g_lf.write( t )
	g_lf.write( "\n\n" )
	return logFile_url 
	# need the string to pass to max, cant find files url from file object

def appendToLog ( data, logFile ):
	logFile.write( data )


def closeLogFile( logDir, msg ):
	global g_lf
	logFile_url = os.path.join (logDir, EXPORT_LOG_FILE)
	# has to be re-openned as we closed this for maxscript/mel
	g_lf = open( logFile_url, 'a' ) 
	appendToLog( msg, g_lf )
	t = strftime( "%a, %d %b %Y %H:%M:%S +0000 ", gmtime() )            
	appendToLog( t, g_lf )
	appendToLog( "\n", g_lf )
	g_lf.close()

#Generate an html file
class HtmlReport(object):
	def __init__(self, logDir):
		if not os.path.exists(logDir):
			os.makedirs(logDir)
		htmlFile_url = os.path.join (logDir, HTML_NAME )
		self.html_file = open( htmlFile_url, 'w' )
		self.html_file.write( "<html><body><h2><center>\n\n" )

	def addToHtml ( self, ref_dir, image_name , message):
		self.html_file.write( "<br><br>\n" )
		self.html_file.write( image_name + " " + message + "\n" )
		self.html_file.write( "<hr>\n" )
		self.html_file.write( "<a href=\"" + ref_dir + "\\" + image_name	\
						+ "\"><img src=\"" + ref_dir + "\\" + image_name	\
						+ "\" height=\"300\"></a>\n" )
		self.html_file.write( "<a href=\"" + image_name + "\"><img src=\"" \
									+ image_name + "\" height=\"300\"></a>\n" )
	def closeHtmlFile( self ):
		self.html_file.write( "</body></html>\n" )
		self.html_file.close()		
			
def fileExportFromList( executable, tbemaxf_url, tbemayaf_url, overw, 	\
			logFileString ):
	MAX_SYSTEM_VARS = ( "3DSMAX_2011_PATH", "3DSMAX_2011x64_PATH", 
		"ADSK_3DSMAX_x32_2012", "ADSK_3DSMAX_x64_2012", "ADSK_3DSMAX_x86_2013", 
		"ADSK_3DSMAX_x64_2013" )
	os.path.normpath(tbemaxf_url)
	# replacing \ with / in maxFilesTxtList for cmd prompt
	tbemaxf_url = tbemaxf_url.replace( "\\", "/" )
	os.path.normpath(tbemayaf_url)
	tbemayaf_url = tbemayaf_url.replace( "\\", "/" )

	#------Max------ 
	# Open Max and call a batch export function that is preloaded on max startup.
	if executable in MAX_EXECUTABLES:
		if not os.environ.has_key(executable):
			print "3dsMax Environment Variable does not exist\n"
			return 1
		basePath = os.environ[executable]
		logFileString = os.path.join( os.getcwd(), DEBUG_LOG_FILE )
		logFileString = logFileString.replace( "\\", "/" )
		
		#set the tests folder as a working directory in 3dsmax
		testFolder = os.path.abspath(os.path.dirname(tbemaxf_url)) 
		projectFolder = os.path.abspath(testFolder + "/../")
		projectFolder = projectFolder.replace( "\\", "/" )
		print "Setting 3dsmax " + MAX_VERSION[executable] \
				+ " working directory to - " + projectFolder
				
		maxCmdString = "3dsmax"
		maxCmdOptions = " -mxs \"BigWorld_Batch_Export \\\"" + tbemaxf_url \
						+"\\\" " + str(1) + " \\\"" + logFileString + "\\\"" \
						+ " \\\"" + projectFolder + "\\\"\"" 
		
		varPathMaxCmdString = os.path.join( basePath, maxCmdString )
		varPathMaxCmdStringOptions = ("\"" + varPathMaxCmdString + "\" " \
										+ maxCmdOptions)
		command = Command(varPathMaxCmdStringOptions)	
		subprocess_output = command.run(timeout=TIMEOUT, program="3dsmax.exe" )

	#-----MAYA------- 
	# Open Maya and call a batch export procedure that is already loaded by its 
	# userSetup.mel script
	else:
		mayaExePath = executable
				
		mayaCmdString = ("\"" + mayaExePath + "\"" 					\
			+ " -command 'BigWorld_Batch_Export(\"" + tbemayaf_url 		\
			+ "\", \"" + str(overw) + "\", \"" + logFileString + "\");\'" ) #Python - dos - mel string literals
		command = Command(mayaCmdString)	
		subprocess_output = command.run(timeout=TIMEOUT, program="maya.exe" )
	
	global additional_error_messages 
	additional_error_messages += subprocess_output
	print subprocess_output	
	print "Complete", "Export complete, Log file created."
	return subprocess_output
	

def verifyPath( sourceName, destName ):		
	#Source folder dose not exists
	if not os.path.exists( sourceName ):
		print "Error: Source directory, %d, is invalid.\n" , sourceName
		return False
	#Source exists but destination doesn't, create destination directory
	elif not os.path.exists( destName ):
		try: 
			os.makedirs( destName )
			return True
		except os.error:
			print "Error: failed to create destination folder %s.\n" , destName
			return False
	else:
		return True
		
def exportDir( executable, sourceName, dest, overw ):

	sourceName = sourceName.replace( "/", "\\" )
	dest = dest.replace( "/", "\\" )
	
	ANIM_EXT = ".animation"
	EXTENSIONS = (".tga", ".jpg", ".dds", ".bmp", ".mfm")
	VIS_ANIM_SETTINGS = (".animationsettings", ".visualsettings")
	ANIM_SETTINGS = ".animationsettings"    

	#Create a log file, and a list of max and maya files to be exported
	tbemaxf_url = createListOfExportFiles( sourceName, 'ListOfMaxFiles.txt' )
	tbemaxf = open( tbemaxf_url, 'w' )
	tbemayaf_url = createListOfExportFiles( sourceName, 'ListOfMayaFiles.txt' )
	tbemayaf = open( tbemayaf_url, 'w' )

	logFileString = createLogFile( sourceName,"\n* Export process started at " )

	#gets all folders + sub full path in form ['C:\\tmp\\1', 'C:\\tmp\\2', 'etc']
	dirArray = list( recursiveDirGen( sourceName ))
	#gets all files + sub, full path, note this will get other file types too.
	fileArray = recursiveFileGen( sourceName )

	#Create a mirror of the source directory folders in dest
	for d in dirArray:
		reldir = os.path.relpath( d , sourceName)
		dir = os.path.join( dest, reldir )
		try:
			if not os.path.exists( dir ):
				os.makedirs( dir )
		except os.error:
			print "Failed to create directory "+ dir \
					+ " in the destination folder\n"
			return 1

	# source directory added to the array of directories to export 
	dirArray.append( sourceName )

	# Copy .visualsettings and .animationsettings file
	# This will be used by the max function to determine if both a .animation 
	# and .visual are require and it will present any options
	# Copy any texture maps    
	for sf in fileArray:
		#check for file extension.
		( fname, extension ) = os.path.splitext( sf )
		if (extension in EXTENSIONS or extension in VIS_ANIM_SETTINGS) and "screenshot" not in sf:
			sfdir = os.path.dirname( sf )
			relative_folders =  os.path.relpath( sfdir , sourceName)
			finalDest = os.path.join( dest, relative_folders)
			shutil.copy( sf, finalDest )

	#change the file array to the specific folder
	if executable in MAX_EXECUTABLES:
		fileArray = list( recursiveFileGen( os.path.join( sourceName, MAX_DIR) ))	
	else:
		fileArray = list( recursiveFileGen( os.path.join( sourceName, MAYA_DIR) ))
		
	# Generate a list of max files and maya files from fileArray
	for sf in fileArray:
		#Get the source and dest
		sfdir = os.path.dirname( sf )
		relative_folders =  os.path.relpath( sfdir, sourceName )
		finalDest = os.path.join( dest, relative_folders)
		sf_with_ext = os.path.basename( sf )
		( fname, extension ) = os.path.splitext( sf_with_ext )
		# The Maxsxcript BigWorld_Startup.ms function 
		# BigWorld_Load_Export_WriteLog will switch export type 
		# (.animation or .visual) depending on extension
		expf = os.path.join( finalDest, fname )

		# Write out the exportfile.txt 
		if extension == ".max" and executable in MAX_EXECUTABLES:
			text = sf + "\n" + expf + VISUAL_EXT
			appendListFile( text.replace( "\\", "/" ), tbemaxf )
			animSetFileString = sfdir + "\\" + fname + ANIM_SETTINGS
			if animSetFileString in fileArray:
				text = sf + "\n" + expf + ANIM_EXT
				appendListFile(text.replace( "\\", "/" ), tbemaxf )
		elif extension == ".ma" and not executable in MAX_EXECUTABLES:
			#Tests for .animationsettings will eventually be required here
			mixedSlash_url = ( sf + "\n" + expf )
			fixedSlash_url = mixedSlash_url.replace( "\\", "/" )
			appendListFile( fixedSlash_url, tbemayaf )
		elif extension == ".mb" and not executable in MAX_EXECUTABLES: 
			mixedSlash_url = ( sf + "\n" + expf )
			fixedSlash_url = mixedSlash_url.replace( "\\", "/" )
			appendListFile( fixedSlash_url, tbemayaf )

	tbemaxf.close()
	tbemayaf.close()
	g_lf.close() #temporarily close log file so mel and max can edit it.

	fileExportFromList( executable, tbemaxf_url, tbemayaf_url, overw, 	\
			logFileString )
	closeLogFile( sourceName, "*** Export process finished at " )

def compareImages( imgPath, imgPath2 ):
	#compare images to 
	IM_RESIZE = (80, 80)
	DIFF_THRESHOLD = 95
	# open the images to compare, resize them, and convert to grayscale
	im1 = Image.open(imgPath).resize(IM_RESIZE).convert("L")
	im2 = Image.open(imgPath2).resize(IM_RESIZE).convert("L")
	# get the rgb values of the pixels in the image
	im1_data = list(im1.getdata())
	im2_data = list(im2.getdata())
	# create an array of the differences in rgb values between the two images
	diff = []
	for num in range(len(im1_data)):
		diff.append(im1_data[num] - im2_data[num])
	# find the total difference in rgb value for all pixels in the images
	diff_val = 0
	for x in diff: 
			diff_val += x
	# adjust DIFF_THRESHOLD for accuracy
	if (abs(diff_val) > 2*DIFF_THRESHOLD):
		print "ERROR: diff value = " +str(diff_val)
		return False
	if (abs(diff_val) > DIFF_THRESHOLD):
		print "WARNING: diff value = " +str(diff_val)
	return True

#run program with a timeout
class Command(object):
	def __init__(self, cmd):
		self.cmd = cmd
		self.process = ""#None

	def run(self, timeout, program):
		def target():
			self.returncode = 0
			try:
				self.subprocess_output = subprocess.check_output( self.cmd, 
										stderr=subprocess.STDOUT, shell=True )
			except subprocess.CalledProcessError, e:
				self.subprocess_output = e.output
				print "WARNING: " + program + " closed with an error " + e.output \
						+ "\n" + self.cmd
				#self.returncode = e.returncode

		start_time = time.time()
		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			try:
				subprocess.check_output("taskkill /im " + program + " /f")
			except subprocess.CalledProcessError, e:
				print "failed to kill " + program
			try:
				#kill windows error message, if any
				subprocess.check_output("taskkill /im WerFault.exe /f")
			except subprocess.CalledProcessError, e:
				pass
			thread.join()
			end_time = time.time()
			timeToRun = end_time - start_time
			self.subprocess_output =  "\nERROR: " + program + " was brutally closed, "\
							+ "TIMEOUT ERROR. Total Time: " + str(timeToRun) + "\n\n"
			self.returncode = 1
		else:
			self.subprocess_output =""
		return self.subprocess_output
		
def createScreenShot( testName, testFolder):
	# Copy the python script to the model editor res folder
	python_script = testName + ".py"
	python_script_path = os.path.join( testFolder, python_script)	
	if not os.path.exists( python_script_path ):
		return "FAILED: couldn't find python script file - " + python_script_path + "\n\n"
	if os.path.exists( os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) ):
		#remove exists
		os.remove( os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) )
	shutil.copy( python_script_path, 
						os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) )
	
	# Copy the layout file
	layout_file = testName + "."+MODEL_EDITOR_LAYOUT_FILE
	layout_file_path = os.path.join( testFolder, layout_file)
	if not os.path.exists( layout_file_path ):
		return "FAILED: couldn't find .layout script file - " + layout_file_path + "\n\n"
	if os.path.exists( MODEL_EDITOR_LAYOUT_FILE ):
		#remove exists
		os.remove( MODEL_EDITOR_LAYOUT_FILE )
	shutil.copy( layout_file_path, MODEL_EDITOR_LAYOUT_FILE )
	
	# Copy the options file
	option_file = testName + "."+MODEL_EDITOR_OPTIONS_FILE
	option_file_path = os.path.join( testFolder, option_file)
	if not os.path.exists( option_file_path ):
		return "FAILED: couldn't find .option script file - " + option_file_path + "\n\n"
	if os.path.exists( MODEL_EDITOR_OPTIONS_FILE ):
		#remove exists
		os.remove( MODEL_EDITOR_OPTIONS_FILE )
	shutil.copy( option_file_path, MODEL_EDITOR_OPTIONS_FILE )
		
	# run model editor and python script
	cmd = os.path.join( MODEL_EDITOR_PATH, MODEL_EDITOR_FILE) + " -unattended -noConversion -s " + testName
	command = Command(cmd)	
	subprocess_output = command.run(timeout=TIMEOUT, program=MODEL_EDITOR_FILE )
		
	#delete the files we've copied
	if os.path.exists( MODEL_EDITOR_OPTIONS_FILE ):
		os.remove( MODEL_EDITOR_OPTIONS_FILE )
	if os.path.exists( MODEL_EDITOR_LAYOUT_FILE ):
		os.remove( MODEL_EDITOR_LAYOUT_FILE )
	if os.path.exists( os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) ):
		os.remove( os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) )
	python_script = testName + ".pyc"
	if os.path.exists( os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) ):
		os.remove( os.path.join( MODEL_EDITOR_SCRIPTS_PATH, python_script) )
	
	if command.returncode != 0:
		return "FAILED: Couldn't take screenshots for " + testName + "\n"\
				+ subprocess_output + "\n"
	
	return "SUCCESS"
	
def compareScreenShots( executable, sourceName, output_folder, version, reportHolder, test_name):

	if version in MAX_EXECUTABLES:
		version = MAX_VERSION[version]
	
	#create a log file for the image comparison
	t = strftime( "%a_%d_%b_%Y_%H_%M_%S", localtime())
	logFile_url = os.path.join \
				(sourceName, t + "_" + version + "_" + IMAGE_COMPARE_LOG_FILE)
	file = open( logFile_url, 'w' )
	failed = 0
	new_screen_shot = 0
	total_files = 0
	text_report = ""
	
	#create a tmp folder to put the new screen shots inside
	if not os.path.exists(os.path.join( os.getcwd(), TMP_FOLDER )):
		os.makedirs(os.path.join( os.getcwd(), TMP_FOLDER ))
	
	# run only on the specific maya/max folder
	if executable in MAX_EXECUTABLES:
		root = os.path.join( sourceName, MAX_DIR)
	else:
		root = os.path.join( sourceName, MAYA_DIR)
	
	if not os.path.exists(root):
		root = sourceName
		
	fileArray =  recursiveFileGen( root )
	
	#for each python file create the screenshots
	for sf in fileArray:
		#check for file extension, search python files
		( fname, extension ) = os.path.splitext( sf )
		if extension == ".py":
			#get test name
			testName = os.path.basename( sf )
			( testName, extension ) = os.path.splitext( testName )
			( testName, extension ) = os.path.splitext( testName )
			sfdir = os.path.dirname( sf )
			#call the create screen shot function
			msg = createScreenShot( testName, sfdir )
			if not "SUCCESS" in msg:
				#print only errors
				failed += 1
				text_report += msg
				print msg
				file.write( msg )
		else:
			continue
			
	#compareScreenShots
	positive_results_folder = os.path.join( output_folder, "positive_results")
	fileArray = recursiveFileGen( os.path.join( os.getcwd(), TMP_FOLDER ))
	dest_folder = os.path.join( output_folder, version)
	
	html_report = HtmlReport( dest_folder )
	
	#compare each screen-shot to the one in the positive_results_folder
	for sf in fileArray:
		#get file name
		image_file = os.path.basename( sf )
		
		positive_results_folder = os.path.join( output_folder, "positive_results")	
		#this test only exported different in 2013 and other max version
		if "test_058_cat_rig_tests" in sf and "3DSMAX_2013" in version:
			positive_results_folder = os.path.join( output_folder, "positive_results_2013")
			
		if not os.path.exists(positive_results_folder):
			os.makedirs(positive_results_folder)
			
		if not os.path.exists( os.path.join( positive_results_folder, image_file) ):
			html_report.addToHtml ( positive_results_folder, image_file , "-new screenShot")
			msg = "WARNING: couldn't find " + image_file \
					 + " screen-shot in the positive_results folder.\n" \
					 + "Saving " + image_file + " as a reference "\
					 + " in the positive_results folder, please re-run the test."
			text_report += msg +"\n\n"
			shutil.move( sf, os.path.join( positive_results_folder, image_file) )
			new_screen_shot +=1 
		else:
			if not compareImages( sf, 
							 os.path.join( positive_results_folder, image_file) ):
				msg = "FAILED: " + image_file \
								+ " screen shots are not similar to the original"
				html_report.addToHtml ( positive_results_folder, image_file , "-FAILED: screen-shots are not similar")
				failed += 1
				text_report += msg +"\n\n"
			else:
				html_report.addToHtml ( positive_results_folder, image_file , "-similar")
				msg = "SUCCESS: " + image_file \
									+ " screen shots is similar to the original"		
		total_files += 1
		print msg
		
	msg = "\n" + str(total_files) + " screen-shots have been created \n" \
			+ str(failed) + " tests failed.\n" + str(new_screen_shot) \
			+ " new screen-shots have been saved as a reference.\n\n" \
			+"please see " + os.path.join( dest_folder, HTML_NAME) + "\n\n"
	text_report += msg
	print msg
	file.write( msg )
	file.close()
	html_report.closeHtmlFile( )
	
	#move images to the screenshots to the screenshot directory
	#delete the tmp folder
	tmp_files = os.path.join( os.getcwd(), TMP_FOLDER )
	fileArray = recursiveFileGen( tmp_files)
	for sf in fileArray:
		image_file = os.path.basename( sf )
		if os.path.exists( os.path.join( dest_folder, image_file) ):
			os.remove( os.path.join( dest_folder, image_file) )
		shutil.move ( sf , dest_folder)
	if os.path.exists(tmp_files):
		shutil.rmtree( tmp_files )
	
	
	reportHolder.finishReport( reporter.Report
			( failed, test_name + " - image comparison    ", text_report, version ) )
	print "Please see " + logFile_url + " for summary\n\n"
	return failed
	
	
def compareVisualFile( testName, version, sourceName, dest ):

	# run only on the specific folder
	if version in MAX_EXECUTABLES:
		#Each 3dsmax version creates a different visual file
		root = os.path.join( sourceName, os.path.join( MAX_DIR, MAX_VISUAL_DIR[version]))
		droot = os.path.join( dest, MAX_DIR )
	else:
		root = os.path.join( sourceName, os.path.join( MAYA_DIR, MAYA_VISUAL_DIR[version]))
		droot = os.path.join( dest, MAYA_DIR)
	if not os.path.exists(root):
		root = sourceName
		droot = dest
		
	fileArray = recursiveFileGen( root )
		
	text = "\nFAILED: couldn't find " +testName+ " converted visual file"
	
	for sf in fileArray:
		#check for file extension.
		( fname, extension ) = os.path.splitext( sf )
		if testName in fname and extension == VISUAL_EXT:
			sfdir = os.path.dirname( sf )
			relative_folders =  os.path.relpath( sfdir , root)
			sf_with_ext = os.path.basename( sf )
			finalDest = os.path.join( droot, relative_folders)
			exported_visual_file = os.path.join( finalDest, sf_with_ext)
			( fname, extension ) = os.path.splitext( sf_with_ext )
			
			#compare source to exported
			if os.path.exists(exported_visual_file ): 
				if filecmp.cmp( sf, exported_visual_file):	
					text = "SUCCESS: " + fname + " converted visual file is "\
							"the same as the source"
				else:
					text = "FAILED: " + fname + " converted visual file is not "\
							"the same as the source"
			else:
				text = "FAILED: couldn't find " +fname+ " converted visual file"
			break;

	return text

#Read a not empty line
def readLineFromLog( f ):
	l = f.readline()
	if not l:
		return l
	while l=="\n" or l=="" or l=="\n"  or l=="\r":
		l = f.readline()
		if not l:
			break
	return l.strip()
	
test_result = ""

def analyseResults( version, sourceName, dest, reportHolder, test_name ):
	total_files = 0
	total_fail = 0
	global test_result
	
	def ouputResults( text ):
		global test_result
		print text
		appendToLog( text, g_lf )
		test_result += text
	
	if version in MAX_EXECUTABLES:
		root = os.path.join( sourceName, MAX_DIR)
	else:
		root = os.path.join( sourceName, MAYA_DIR)
	result_file_path = os.path.join( root, RESULTS_LOG_FILE)
	logFileString = createLogFile( sourceName, "\n***" )
	
	try:
		debug_log_file = open( DEBUG_LOG_FILE , 'r' )
	except os.error:
		text = "\nError: Cannot open " + DEBUG_LOG_FILE
		ouputResults( text )
		closeLogFile( sourceName, "\n***" )
		return 1

	while 1:
		#go over the debug.log file
		line = readLineFromLog(debug_log_file)
		if not line: #EOF
			break
		if "SUCCESSFULLY" in line or "ERROR" in line or "FAIL" in line \
			or "WARNING" in line:
			continue
		elif (".mb" in line or ".ma" in line or ".visual" in line ) and \
				( not ".animation" in line ): 
			#test
			total_files += 1
			fname = os.path.basename( line )
			( fname, extension ) = os.path.splitext( fname )
			
			text = "\n\n" + fname + "\n" + \
					"========================================"+"\n"
			ouputResults( text )
			
			#search the test in the results file
			test = ""
			output_file = open(	result_file_path , 'r')
			while 1:
				l = readLineFromLog(output_file)
				if not l:
					#EOF
					break
				if (l+".") in line:
					test = l
					break

			if test == "":
				total_fail += 1
				text = "\nFAILED: couldn't find " + fname + \
					" results in the results.log file\n\n"
				ouputResults( text )
				output_file.close()
			else:
				ex_res = readLineFromLog(output_file)
				output_file.close()
				line = readLineFromLog(debug_log_file)
				if not line: #EOF
					text = "FAILED: Test expected result is not as expected\n" +\
							"Result: " + line
					ouputResults( text )
					total_fail += 1
					break
								
				if ex_res in line:
					if "ERROR" in line:
						line = readLineFromLog(debug_log_file)
						if not "FAIL" in line:
							text = "FAILED: Test was expected to fail, " + \
									"not to succeed"
							ouputResults( text )
							total_fail += 1
							continue
							
					if "WARNING" in line:
						line = readLineFromLog(debug_log_file)
						if not "SUCCESSFULLY" in line:
							text = "FAILED: Test was expected to succeed, " + \
									"not to fail"
							ouputResults( text )
							total_fail += 1
							continue
					
					text = "SUCCESS\n Output: " + ex_res + " as expected.\n"
					ouputResults( text )
					
					if not "_anim" in test:
						#make a .visual comparison
						visual_text = compareVisualFile(test, version, sourceName, dest)
						if "SUCCESS" in line:
							if not "SUCCESS" in visual_text:
								ouputResults( visual_text )
								total_fail += 1
								continue
						else:
							if not "FAILED: couldn't find" in visual_text:
								text = "Error, .visual file was created"
								ouputResults( text )
								total_fail += 1
								continue
							else:	
								visual_text = "SUCCESS: .visual file wasn't created"
							
						ouputResults( visual_text )
					
				else:
					text = "FAILED: Test expected result wasn't as expected\n"+\
						"Result: " + line
					ouputResults( text )
					total_fail += 1
					continue	
	text = "\n\n" + str(total_files) + " tests total\n\n" + str(total_fail) + \
			" tests failed.\n"
			
	ouputResults( text )
	closeLogFile( sourceName, "\n***" )
	global additional_error_messages
	if additional_error_messages != "" :
		test_result += additional_error_messages
		additional_error_messages = ""
		reportHolder.finishReport( reporter.Report
						( -1, test_name + " - exporting   ", test_result, version ) )
		return 1
	if total_files > 0:
		reportHolder.finishReport( reporter.Report
				( total_fail, test_name + " - exporting   ", test_result, version ) )
		return total_fail
	test_result += "FAILED: no files has been exported"
	reportHolder.finishReport( reporter.Report
						( -1, test_name + " - exporting   ", test_result, version ) )
	return 1

def runInternalTest( executable, destName, output_folder, version, options ):
	overWrite = 1
	res = 0
	if ( None == options.sourceName ):
		options.sourceName = os.getcwd()
			
	if ( None == destName ):
		destName = os.getcwd()
	
	reportHolder = reporter.ReportHolder( "Automated Testing",
			"%s on %s" % ( options.name, version ),options.email  )
	
	if verifyPath( options.sourceName, destName ) :
		deleteLogFile( options.sourceName )
		#export files
		exportDir( executable, options.sourceName, destName, overWrite )
		#analyse the results, return number of failed tests
		res = analyseResults( version, options.sourceName, destName, reportHolder, options.name )
		#rename log files
		backUpLogFile( options.sourceName, version )
		if ( options.image == True):
			#create screen shots
			res += compareScreenShots( executable, options.sourceName, output_folder, version, \
					reportHolder, options.name )
	else:
		print "error \n"
		
	reportHolder.buildUrl = options.url
	reportHolder.sendMail()
	return res

def changePerferenceSettings(settingsFolder):
	orgFile = os.path.join(MODEL_EDITOR_RES_PATH, GRAPHICS_PREFERENCES_FILE)
	newFile = os.path.join(settingsFolder, GRAPHICS_PREFERENCES_FILE)
	if os.path.exists(orgFile):
		shutil.copy( orgFile, orgFile + "_bk" )
	shutil.copy( newFile, orgFile )
	
def revertPerferenceSettings():
	file = os.path.join(MODEL_EDITOR_RES_PATH, GRAPHICS_PREFERENCES_FILE)
	if os.path.exists(file + "_bk"):
		os.remove(file)
		shutil.copy( file + "_bk", file )

def runTests():
	usage = "\n3DSMAX:" + \
			"\n%prog -s [source directory] -f [Fantasydemo directory] " + \
			"-x [3DMax executable]\n"\
			"\nMAYA:" + \
			"\n%prog -s [source directory] -f [Fantasydemo directory] " + \
			"-m [Maya's executables path] -v [Maya's executables version]\n"
	
	parser = optparse.OptionParser( usage )
	
	parser.add_option( "-s", "--source",
			dest = "sourceName", default=None,
			help = "Source directory for the imported files\n" )

	parser.add_option( "-f", "--fantasydemo",
			dest = "fantasydemo", default=None,
			help = "Fantasydemo directory for the exported files\n" )

	parser.add_option( "-m", "--maya",
			dest = "maya_path", default=None,
			help = "Set Maya's executables path\n")
	
	parser.add_option( "-v", "--mayaVersion",
			dest = "mayaVersion", default=None,
			help = "Set Maya's executable version:\n" + \
					"|".join( MAYA_VERSION )+"\n")
			
	parser.add_option( "-x", "--max",
			dest = "max_exec", default=None,
			help = "3DMax executables:\n" + "|".join( MAX_EXECUTABLES )+"\n")

	parser.add_option( "-i", "--image",
			dest = "image", default=True,
			help = "--image=False will cancel the Image comparison\n")
	
	parser.add_option( "-u", "--url",
					dest = "url", default=None,
					help = "The URL for the results in jenkins" )
	
	parser.add_option( "-c", "--clear",
					dest = "clear", default=False,
					help = "--clear=True will clear the " + 
							"Fantasydemo\res\exporter_test_files folder " + 
							"for this specific max/maya version" )

	parser.add_option( "-n", "--name",
				dest = "name", default="Exporters test",
				help = "Set the test name in the subject of the report e-mail " )
				
	parser.add_option( "-e", "--email",
				dest = "email", default=reporter.EMAIL_ADDRESSES,
				help = "Set the mailing list the report will be sent to. " +
						"Comma-separate multiple addresses")
	 
	(options, args) = parser.parse_args() 
	
	if None == options.sourceName:
		print "\nPlease specify the source directory\n"
		parser.print_help()
		return 1
	
	if None == options.fantasydemo:
		print "\nPlease specify the Fantasydemo directory\n"
		parser.print_help()
		return 1
	
	#Set destination folder for the exported files, must be in the res folder
	dest = os.path.join( options.fantasydemo, "exporter_test_files")  
	
	if options.clear:
		if options.max_exec in MAX_EXECUTABLES:
			if os.path.exists( os.path.join( dest, MAX_DIR) ):
				print "Deleting " + os.path.join( dest, MAX_DIR)
				shutil.rmtree( os.path.join( dest, MAX_DIR) )
		else:
			if os.path.exists( os.path.join( dest, MAYA_DIR) ):
				print "Deleting " + os.path.join( dest, MAYA_DIR)
				shutil.rmtree( os.path.join( dest, MAYA_DIR) )

	output_folder = os.path.join( options.sourceName, "screenshot")
	settingsFolder = os.path.join( options.sourceName, "settings")
	
	changePerferenceSettings(settingsFolder)
	
	res = 0
	
	if options.max_exec in MAX_EXECUTABLES:
		global DEBUG_LOG_FILE
		output_folder = os.path.join( output_folder, "3dsmax")
		DEBUG_LOG_FILE = os.path.join( dest, DEBUG_LOG_FILE )
		res = runInternalTest( options.max_exec, dest, output_folder, \
								options.max_exec, options )
	elif None != options.max_exec:
		print "\n" + options.max_exec + " is not a valid 3Dmax executable\n"
		parser.print_help()
		res = 1
		
	elif None != options.maya_path :
		if ( not options.mayaVersion in MAYA_VERSION ):
			print "\nYou must supply a version for Maya's executable\n"
			parser.print_help()
			res = 1
		else:
			output_folder = os.path.join( output_folder, "maya")
			res =  runInternalTest( options.maya_path, dest, output_folder, \
									options.mayaVersion, options )
	elif None == options.max_exec:
		print "\nYou need to supply a 3dMax executable, or a Maya exe file\n"
		parser.print_help()
		res = 1
	
	revertPerferenceSettings()
	return res
	
	
if __name__ == "__main__":
	sys.exit( runTests() )