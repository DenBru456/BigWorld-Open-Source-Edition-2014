import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"))
import time
import optparse
import create_list
import create_build_number_list
import actions
from log import *
from filter import *
from revision_control import *

if sys.platform.startswith('win'):
	BUILDARCHIVE_PATH="//ba01/BuildArchive"
else:
	BUILDARCHIVE_PATH="/bigworld/ci_buildarchive/"

BIGWORLD_DIR = os.path.realpath(__file__).split("game")[0]
CLIENT = "client"
TOOLS = "tools"
SERVER = "server"
LOCAL = "local"
EMPTY_VALUE = -10
LOCAL_BUILD = -1

def getInputFromUser(options):

	def askUserForInput(min, max):
		#keep ask from the user to choose a number
		input = EMPTY_VALUE
		while input < min or input > max:
			print		
			try:
				input = int(raw_input('Please choose from ' 
						+ str(min) + ' to ' + str(max) +'\n'))
			except ValueError:
				input = EMPTY_VALUE
				continue
		return input
	
	def getChangelistNumber( list, buildNum ):
		buildArray = []
		for build in list:
			if str(build.getBuildNumber()) == str(buildNum):
				return build.getTriggerBuild()
		return 0	
	
	def getBuildName( type ):
		buildArray = []
		i = 1
		buildList = create_list.buildList(type)
		for dir in buildList:
			print "[" + str(i) + "]" + dir.split(".xml")[0]
			buildArray.append(dir.split(".xml")[0])
			i += 1
		return buildArray[askUserForInput(1, len(buildArray)) - 1]
		
	def getBuildNumber( list, buildName ):
		buildArray = []
		i = 1
		print "[0] | Keep local files"
		for build in list:
			print "[" + str(i) + "] " + str(build.getBuildNumber()) + " (" +str(build.getTriggerBuild()) + ")  |  %s" % build.getDate()
			buildArray.append(build.getBuildNumber())
			i += 1		
		choice = askUserForInput(0,len(buildArray))
		if 0 == choice:
			return LOCAL_BUILD		
		return buildArray[choice - 1]
	def setBuildNumber(text , buildNumber, list, buildName):
		if EMPTY_VALUE == buildNumber:
			print text
			return getBuildNumber(list, buildName)
		elif buildNumber == 0:
			return LOCAL_BUILD
		elif buildNumber == -1:
			return len(list) - 1	
		
		for build in list:
			if (build.getBuildNumber()).startswith(str(buildNumber) + "_"):
				return build.getBuildNumber()
		print "	ERROR: couldn't find build number " + buildNumber
		return LOCAL_BUILD
			
	appType = options.appType
	buildName = options.buildName
	serverBuildNumber = options.serverBuildNumber
	clientBuildNumber = options.clientBuildNumber
	toolsBuildNumber = options.toolsBuildNumber
	perforce = options.perforce
	
	changelistNumber = 0
	
	
	if appType == EMPTY_VALUE:
		print "What do you want to copy?"
		buildList = ["Client and Tools", "Server"]
		i = 1
		for type in buildList:
			print "[" + str(i) + "]" + type
			i += 1
		appType = buildList[askUserForInput(1, len(buildList)) - 1]	

	if appType.lower() == "server" :
		#------------------- select server build -----------
		if EMPTY_VALUE == buildName:
			print "Please select a server build"
			buildName = getBuildName(SERVER)
		
			
		#-------------------server build number -----------
		serverList = create_build_number_list.createBuildsArray(os.path.join(BUILDARCHIVE_PATH,buildName))
		serverBuildNumber = setBuildNumber("Please select a server build number", serverBuildNumber, serverList, buildName)
		changelistNumber = getChangelistNumber(serverList, serverBuildNumber)
	
	else:
		#-------------------select Client and tools build-----------
		if EMPTY_VALUE == buildName:
			print "Please select a client and tools build"
			buildName = getBuildName(CLIENT)
				
		#-------------------client build number -----------
		clientList = create_build_number_list.createBuildsArray(os.path.join(BUILDARCHIVE_PATH,buildName + "_client" ))
		clientBuildNumber = setBuildNumber("Please select a client build number", clientBuildNumber, clientList, buildName)
		changelistNumber = getChangelistNumber(clientList, clientBuildNumber)

		#-------------------tools build number -----------
		toolsList = create_build_number_list.createBuildsArray(os.path.join(BUILDARCHIVE_PATH,buildName + "_tools" ))
		toolsBuildNumber = setBuildNumber("Please select a tool build number", toolsBuildNumber, toolsList, buildName)
		changelistNumber = max(changelistNumber,getChangelistNumber(toolsList, toolsBuildNumber))
	
		
	
	if perforce == EMPTY_VALUE:
		#-------------------set p4 update flag -----------
		#ask to set perforce only if it is installed from the command line
		perforceObj =  Perforce()
		if perforceObj.validatePerforce():
			while True:
				p4Flag = str(raw_input("Do you want to perforce to sync " + perforceObj.getWorkspace() + " ? y/n\n"))
				if p4Flag == "y":
					break
				if p4Flag == "n":
					perforceObj = None
					break
	elif perforce.lower() == "true":
		perforceObj =  Perforce()	
	else:
		perforceObj = None
		

			
	return [buildName, serverBuildNumber, clientBuildNumber, toolsBuildNumber, perforceObj, changelistNumber]

def changeActionList(actionList):
	delete = []
	copy = []
	for k in actionList.actionList:
		if k.returnActionType() == actions.DELETE_ACTION:
			delete.append(k)
		else:
			copy.append(k)

	input = EMPTY_VALUE
	while input != 0:
		print
		copyIndex = 0
		for k in copy:
			copyIndex+=1
			print "[" + str(copyIndex) + "] " + k.description()
		
		delIndex = copyIndex
		for f in delete:
			delIndex+=1
			print "[" + str(delIndex) + "] " + f.description()
		print
		
		try:
			input = int(raw_input('Enter a number to remove an action: (0 to continue)'))
		except ValueError:
			continue
		
		if input<= delIndex :
			if input<= copyIndex:
				if input>0:
					print "cancel " + copy[input-1].description()
					del copy[input-1]
			else:
				print
				print "cancel " + delete[input-1  - copyIndex].description()
				print
				del delete[input-1 - copyIndex]
		else:
			continue
	
	finalActionList = actions.ActionList()
	for k in delete:
		finalActionList.append(k)
	for k in copy:
		finalActionList.append(k)
	return finalActionList
			
def bw_get_binaries():

	usage = "\n%prog -s [source directory] -f [Fantasydemo directory] " 
	
	parser = optparse.OptionParser( usage )
	

	perforce = EMPTY_VALUE
	
	parser.add_option( "--appType",
			dest = "appType", default=EMPTY_VALUE,
			help = "specify if you want to build the server, or client and tools\n" )
			
	parser.add_option( "--buildName",
			dest = "buildName", default=EMPTY_VALUE,
			help = "specify the build name\n" )
		
	parser.add_option( "--serverBuildNumber",
			dest = "serverBuildNumber", default=EMPTY_VALUE,
			help = "specify the server build number, 0 for not copy the server, -1 for latest\n" )

	parser.add_option( "--clientBuildNumber",
			dest = "clientBuildNumber", default=EMPTY_VALUE,
			help = "specify the server build number, 0 for not copy the client, -1 for latest\n" )
			
	parser.add_option( "--toolsBuildNumber",
			dest = "toolsBuildNumber", default=EMPTY_VALUE,
			help = "specify the server build number, 0 for not copy the tools, -1 for latest\n" )
			
	parser.add_option( "--syncPerforce",
			dest = "perforce", default=EMPTY_VALUE,
			help = "specify true or false to sync perforce\n" )
			
	parser.add_option( "--noPrompt",
			action = "store_true",
			dest = "noPrompt", default=False,
			help = "Don't ask to modify the actions list\n" )
			
	 
	(options, args) = parser.parse_args() 

	(build,serverBuildNumber,clientBuildNumber, toolsBuildNumber, perforceObj, changelist) = getInputFromUser(options)	

	actionList = create_list.makeList(BUILDARCHIVE_PATH, BIGWORLD_DIR, build, clientBuildNumber, toolsBuildNumber, serverBuildNumber, FilterList() )	

	if not options.noPrompt:
		actionList = changeActionList(actionList)	
	
	if ( perforceObj != None ):
		perforceObj.run( changelist, FormattingPrinter(output = CombinedOutput()))
		
	actionList.execute(FormattingPrinter(output = CombinedOutput()))
	

if __name__ == "__main__":
	sys.exit( bw_get_binaries() )