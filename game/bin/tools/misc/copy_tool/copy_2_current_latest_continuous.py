import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"))
import create_list
import tkMessageBox
import actions
from log import *
from filter import *

CLIENT_SERVER = os.path.join( "//ba01", "BuildArchive" )
BIGWORLD_DIR = os.path.realpath(__file__).split("game")[0]
def getLatestBuildNumber(buildPath):
	buildNumber = -1
	for dir in os.listdir(buildPath):
		try:
			# ignore directory which are not a number
			int(dir)
		except ValueError:
			continue
		if int(dir) > buildNumber:
			buildNumber = int(dir)
	return buildNumber

result = tkMessageBox.askquestion("Warning", "This script will:\n" \
			+ "* Update your SVN repository\n"\
			+ "* Copy the binaries from the latest successful continuous build\n" \
			+ "* This script won't sync your perforce workspace\n" \
			+ " Are you sure you want to continue?", icon='warning')
if result == 'yes':
	buildName = "windows_2_current_2012_continuous"	
	clientNumber = getLatestBuildNumber(os.path.join(CLIENT_SERVER, buildName + "_client"))
	toolsNumber = getLatestBuildNumber(os.path.join(CLIENT_SERVER, buildName + "_tools"))
	serverNumber = -1

	actionsList = create_list.makeList(CLIENT_SERVER, BIGWORLD_DIR, buildName, clientNumber, toolsNumber, serverNumber, FilterList() )

			
	actionsList.execute( FormattingPrinter(output = CombinedOutput()))
