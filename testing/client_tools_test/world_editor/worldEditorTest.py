import os
import sys
import shutil
import stat
import xml.etree.ElementTree as ET
import subprocess
import time
import datetime
import threading
from itertools import izip
from PIL import Image
import socket
import optparse

TEST_SPACES =["highlands", "08_ruinberg"] #"highlands", 08_ruinberg 18_cliff 15_komarin

PACKAGE_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", "..", "..")
SPACES_DIR = os.path.join(PACKAGE_ROOT, "game", "res", "fantasydemo", "spaces" )
LOCATION_XML_FILE = "locations.xml"
DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data")
SCRIPT_DIR = os.path.join(PACKAGE_ROOT, "game", "bin", "tools", "worldeditor", "resources", "scripts")
TEST_FILE = "WorldEditorTestScript.py"
WORLDEDITOR_EXE =  os.path.join(PACKAGE_ROOT, "game", "bin", "tools", "worldeditor", "win64", "worldeditor.exe")

TIMEOUT = 900
DATE_TIME = datetime.datetime.now()

def setPicDir( name ):
	global IMAGES_DIR 
	global REFERENCE_DIR
	global PIC_DIR
	IMAGES_DIR = os.path.join("\\\\ba01", "buildarchive", "worldeditor_test", name, socket.gethostname() )
	REFERENCE_DIR = os.path.join(IMAGES_DIR, "worldEditorTestReferenceDir") #make sure it's outside our working directory
	PIC_DIR = os.path.join(IMAGES_DIR, "%s_%s_%s-%s_%s" %(DATE_TIME.day, DATE_TIME.month, DATE_TIME.year, DATE_TIME.hour, DATE_TIME.minute))

def setWotEnv():
	global SPACES_DIR 
	global SCRIPT_DIR
	global WORLDEDITOR_EXE
	SPACES_DIR = os.path.join(os.getcwd(), "..", "..", "..", "tankfield", "res", "spaces")
	SCRIPT_DIR = os.path.join(os.getcwd(), "resources", "scripts" )
	WORLDEDITOR_EXE =   os.path.join(os.getcwd(), "worldeditor.exe")

def compareImage(img1, img2): 
	notes = ""
	i1 = Image.open(img1)
	i2 = Image.open(img2)
	if not i1.mode == i2.mode:
		notes += "Different kinds of images."
		return (1, notes)
		
	if not i1.size == i2.size:
		notes += "Different sizes."
		return (1, notes)
	 
	pairs = izip(i1.getdata(), i2.getdata())
	if len(i1.getbands()) == 1:
		# for gray-scale jpegs
		dif = sum(abs(p1-p2) for p1,p2 in pairs)
	else:
		dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
	 
	ncomponents = i1.size[0] * i1.size[1] * 3
	difference = (dif / 255.0 * 100) / ncomponents
	notes += "Difference : %3.7f"% (difference)
	if difference > 0.0099:
		return (1, notes)
	return (0, notes)
	
	
#run program with timeout
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
				self.returncode = e.returncode

		start_time = time.time()
		thread = threading.Thread(target=target)
		thread.start()

		thread.join(timeout)
		if thread.is_alive():
			subprocess.check_output("taskkill /im " + program + " /f")
			thread.join()
			end_time = time.time()
			timeToRun = end_time - start_time
			self.subprocess_output =  "TIMEOUT ERROR. Total Time: " + str(timeToRun)
			self.returncode = 1
			
		return self.subprocess_output
		
		
def deleteIfExists( file ):
	if os.path.exists(file):
		os.chmod( file, stat.S_IWRITE )
		if os.path.isdir(file):
			shutil.rmtree(file)	
		else:
			os.remove(file)
		print "Delete " + file
		
def changeTestFile(location):
	deleteIfExists(os.path.join(SCRIPT_DIR, TEST_FILE))
	sourceFile = open(os.path.join(DATA_DIR, TEST_FILE), "r")
	sourceLines = sourceFile.readlines()
	sourceFile.close()
	destFile = open(os.path.join(SCRIPT_DIR, TEST_FILE), "w")
	destFile.write("LOCATION = \"%s\"\n" % location)
	for line in sourceLines:
		destFile.write( line )
	destFile.close()
		
def runTest(spaceName):
	summary = []
	locationXml = os.path.join(SPACES_DIR,spaceName,LOCATION_XML_FILE)
	if not os.path.exists(locationXml):
		print "Error: couldn't find \n%s\nplease make sure this file exists" % os.path.abspath(locationXml)
		return summary
		
	locations = []
	
	tree = ET.parse(locationXml)
	root = tree.getroot()
	for bookmark in root.findall('bookmark'):
		name = (bookmark.find('name').text).strip()
		print "Adding " + name
		locations.append(name)
		
	for location in locations:
		changeTestFile(location)
		spaceOptionsFile = os.path.join(DATA_DIR, spaceName + "_worldeditor.options")
		if not os.path.exists(spaceOptionsFile):
			print "please add a %s_worldeditor.options to %s" %(spaceName, DATA_DIR)
			return summary
			
		cmd = "%s -noConversion -unattended --script %s --options %s" % (WORLDEDITOR_EXE , TEST_FILE.split(".py")[0] , spaceOptionsFile)
		
		img = location + ".bmp"
		deleteIfExists(img)
		
		command = Command(cmd)
		print
		print cmd
		print
		
		subprocess_output = command.run(timeout=TIMEOUT, program="worldeditor.exe" )
		
		if not os.path.exists(img):
			print "Error, WorldEditor didn't create image\n"
			print img
			print "\n\n" + subprocess_output + "\n\n"
			summary.append( Summary(spaceName, location, 1, "Image was not created.") )
			return summary		
		
		refImage = os.path.join(REFERENCE_DIR, spaceName, img)
		
		if not os.path.exists(refImage):
			shutil.move(img, refImage)
			
			print "No reference file for %s, re-runnig the test" % location
			print "file %s\n" % refImage
			
			subprocess_output = command.run(timeout=TIMEOUT, program="worldeditor.exe" )		
			
		(status, notes) = compareImage(refImage, img)
		if status:
			if not os.path.exists(os.path.join(PIC_DIR, spaceName + "_failed")):
				os.makedirs(os.path.join(PIC_DIR, spaceName + "_failed"))
			shutil.copy(img, os.path.join(PIC_DIR, spaceName + "_failed", img))
			shutil.copy(refImage, os.path.join(PIC_DIR, spaceName + "_failed", img.replace(".bmp", "_ref.bmp")))
		shutil.move(img, os.path.join(PIC_DIR, spaceName, img))
		results = Summary(spaceName, location, status, notes)
		print results
		summary.append( results )
		
		# res = command.returncode
		
	return summary
		
class Summary():
	def __init__(self, spaceName, location, status, notes):
		self._spaceName = spaceName
		self._location = location
		self._status = status
		self._notes = notes
	
	def __str__(self):
		if self._status:
			return "Failed %s  %s  %s" % (self._spaceName, self._location, self._notes)
		return "Succeed %s  %s  %s" % (self._spaceName, self._location, self._notes)
	
	def getStatus(self):
		return self._status	
		
def runScript():
	errors = False
	
	usage = "usage: %prog [options]"
	
	parser = optparse.OptionParser( usage )
	parser.add_option( "--wot",
						action = "store_true",
						dest = "wot", default=False,
						help = "run wot worldeditor\n\
								when setting this flag, you must run the test from:\n\
								game\\bigworld\\tools\\worldeditor" )
								
	parser.add_option( "--branch_name",
						dest = "branch_name", default="local",
						help = "Change the location the images are saved\n\
								default=local" )
								
	parser.add_option( "--spaces",
			dest = "spaces", default=None,
			help = "specify the spaces you want to test, separated by semicolons\n\
					default - %s\n" % ";".join(TEST_SPACES))
			
	(options, args) = parser.parse_args()
	
	setPicDir(options.branch_name)
	
	if options.wot:
		print "Testing Wot\n"
		setWotEnv()
	else:
		print "Testing BW\n"
		
	spaces = TEST_SPACES
	if options.spaces != None:
		spaces = (options.spaces).split(";")
	
	summary = []
	if not os.path.exists(REFERENCE_DIR):
		os.makedirs(REFERENCE_DIR)
	if not os.path.exists(PIC_DIR):
		os.makedirs(PIC_DIR)
		
	for spaceName in spaces:
		if not os.path.exists(os.path.join(REFERENCE_DIR, spaceName)):
			os.mkdir(os.path.join(REFERENCE_DIR, spaceName))
		if not os.path.exists(os.path.join(PIC_DIR, spaceName)):
			os.mkdir(os.path.join(PIC_DIR, spaceName))
			
		testSummary = runTest(spaceName)
		if not testSummary == []:
			summary += testSummary
		else:
			errors = True
			break
		
	for result in summary:
		print result
		errors = errors or result.getStatus()
		
	print "please check %s for the images" % IMAGES_DIR
	print errors
	return errors

		
if __name__ == "__main__":
	sys.exit( runScript() )