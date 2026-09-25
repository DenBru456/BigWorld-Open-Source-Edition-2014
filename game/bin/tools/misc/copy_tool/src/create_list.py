import time
import os
import sys
from xml.dom.minidom import parse

import actions
from filter import *

CLIENT = "client"
TOOLS = "tools"
SERVER = "server"
XML_DIR = os.path.join( os.path.dirname(os.path.realpath(__file__)),".." , "xml_config_files" )

def returnListFilesFromPath(node, location):
	# get lists of relative path files from the xml
	array = []
	for child in node:
		if child.nodeName == "type":
			if "*" in child.attributes["file"].value:
				( srcdir, extension ) = os.path.split(
												child.attributes["file"].value )
				fullPath = os.path.join(location, srcdir)
				extension = extension.split("*")[-1]
				for basename in os.listdir(fullPath):
					if basename.endswith(extension) and ("_d"+extension) not in basename:
						pathname = os.path.join(srcdir, basename)
						array.append(pathname)
			else:		
				array.append(child.attributes["file"].value)
		else :
			print "Error While parsing in XML"
	return array
		
def generateActionsList( type, xmlFile, destDir, location ):
	#going over the xml file, and create a list of actions- copy files, keep, or delete
	copyArray = []

	tree = parse( xmlFile )
	root = tree.getElementsByTagName("root")[0]
	for action in root.childNodes:
		if action.nodeName == type:
			copyArray = returnListFilesFromPath( action.getElementsByTagName( "type" ), location )
	
	return copyArray	

def buildList( type = "" ):
	#return list of xml files for the client/server
	perfix = ""
	if type == CLIENT:
		perfix = "windows_"
	elif type == SERVER:
		perfix = "linux64_"
	
	buildList = []
	for file in os.listdir(XML_DIR):
		if file.startswith(perfix) and file.endswith(".xml"):
			buildList.append(file)
			
	return  buildList

def makeList(bwServer, destDir, buildName, clientBuildNumber, toolsBuildNumber, serverBuildNumber , filterList = FilterList(), serverBuildName = None):
	# give it a build name and client/server and tools number
	# it return a copy and delete array
	clientArray = []
	toolsArray = []
	serverArray = []

	#generate server actions list
	if serverBuildName == None:
		serverBuildName = buildName
		
	if serverBuildNumber > -1:	
		serverXmlFile = os.path.join( XML_DIR, serverBuildName + ".xml" )
		if not os.path.exists(serverXmlFile):
			print "Error: Can't find " + serverXmlFile
		else:
			serverArray = generateActionsList( SERVER, serverXmlFile, destDir, os.path.join(bwServer, serverBuildName, str(serverBuildNumber)) )	
	
	#generate client tools actions list	
	if clientBuildNumber > -1 or toolsBuildNumber > -1:
		clientXmlFile = os.path.join( XML_DIR, buildName + ".xml" )
		if not os.path.exists(clientXmlFile):
			print "Error: Can't find " + clientXmlFile
		else:
			#generate actions list
			if clientBuildNumber > -1:
				clientArray = generateActionsList( CLIENT, clientXmlFile, destDir, os.path.join(bwServer, buildName + "_client", str(clientBuildNumber)) )	
			if toolsBuildNumber > -1:
				toolsArray = generateActionsList( TOOLS, clientXmlFile, destDir, os.path.join(bwServer, buildName + "_tools", str(toolsBuildNumber)) )

	#combine lists into one list
	serverBuild = actions.SourcePath(os.path.join(bwServer, serverBuildName, str(serverBuildNumber)), SERVER)
	clientBuild = actions.SourcePath(os.path.join(bwServer, buildName + "_client", str(clientBuildNumber)), CLIENT)
	toolsBuild = actions.SourcePath(os.path.join(bwServer, buildName + "_tools", str(toolsBuildNumber)), TOOLS)
	actionList= actions.ActionList()
	
	for f in serverArray:
		if filterList.check(f):
			actionList.append(actions.CopyAction(f, destDir, serverBuild))
	for f in (set(clientArray) - set(serverArray)):	
		if filterList.check(f):
			actionList.append(actions.CopyAction(f, destDir, clientBuild))
	for f in (set(toolsArray) - set(serverArray + clientArray)):
		if filterList.check(f):
			actionList.append(actions.CopyAction(f, destDir, toolsBuild))

	return actionList

