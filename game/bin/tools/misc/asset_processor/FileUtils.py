import os
import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from LogFile import errorLog

import xml.dom.minidom


def getResourcePaths():
	dom = xml.dom.minidom.parse( file("paths.xml") )
	
	pathParent = dom.getElementsByTagName("Paths")[0]
	paths = pathParent.getElementsByTagName("Path")

	ret = []	
	for pathElement in paths:
		path = pathElement.childNodes[0].data		
		ret.append( os.path.abspath( path ) + "\\" )
		
	return ret

#This function is needed because we cannot use ResMgr to save
#out non-xml effect files.  Thus we need to grab the first res path 
#from paths.xml in order to save files using the os module and absolute paths.
def findFirstResPath():
	return getResourcePaths()[0]
	
	
#Remove extension from the given filename
def stripExtension(name):
	idx = name.rfind(".")
	if idx != -1:
		return name[:idx]
	return name
	
	
#Return the extension from the given filename
def extension(name):
	try:
		return name[name.rindex(".")+1:]
	except ValueError:
		return ""


#Return the path name (without trailing slash) or return ""
def extractPath(name):
	idx = name.rfind("/")
	if idx == -1:
		idx = name.rfind("\\")
		if idx == -1:
			return ""
	return name[:idx]
	
	
#Return just the filename.
def stripPath(name):
	idx = name.rfind("/")
	if idx == -1:
		idx = name.rfind("\\")
		if idx == -1:
			return name
	return name[idx+1:]
	
	
#Prepend the res search path onto the filename
#Note - does not ensure file exists
def fullName(name):
	return BW_RES_PATH + name

		
def extractSectionsByName(sect,name):
	sects = []
	for i in sect.items():
		#print i[0]
		if i[0] == name:
			sects.append(i[1])
	return sects
	
def openSectionFromFolder(filename):
	path = extractPath(filename)
	path = path.replace("\\","/")
	name = stripPath(filename)
	pathSect = ResMgr.openSection(path)
	if pathSect == None:
		errorLog.errorMsg( "Error opening %s" % (path,) )
		return (None,None)
	sect = pathSect[name]
	return (sect,path)
	
	
BW_RES_PATH = findFirstResPath()