import os
import time
import datetime

P4_CHANGELIST_NUMBER_FILE = "p4_changelist_number.txt"

class BuildDir:
	def __init__( self, triggerBuild, buildNumber, date ):
		self._triggerBuild = triggerBuild
		self._buildNumber = buildNumber
		self._date = date
		
	def getBuildNumber( self ):
		return self._buildNumber
		
	def getTriggerBuild( self ):
		return self._triggerBuild
		
	def getDate( self ):
		return self._date
		
	def getStrptime( self ):
		return datetime.datetime(*(time.strptime(self.getDate(), 
										"%a %b %d %H:%M:%S %Y")[0:6]))
		
	def __eq__( self, other ):
		
		if not (self.getBuildNumber() == other.getBuildNumber()):
			return False

		if not (self.getTriggerBuild() == other.getTriggerBuild()):
			return False
		if not (self.getDate() == other.getDate()):
			return False
		return True
		
	def __lt__ (self, other): 
		return self.getStrptime() < other.getStrptime()
		
	def __str__ (self):
		return str(self._triggerBuild) + " " + str(self._buildNumber) + " " + str(self._date)
		
def createBuildDir(path, dirNum):
	dirPath = os.path.join(path, dirNum)
	buildNumber = dirNum
	if "linux" in dirPath:
		for basename in os.listdir(dirPath):
			buildNumber = os.path.join(dirNum, basename)
		dirPath = os.path.join(path, buildNumber)
		
	date = time.ctime(os.path.getctime(dirPath))
	changeListNumber = 0
	
	for file in os.listdir(dirPath):
		if file.startswith("p4_changelist_number_"):
			changeListNumber = int((file.split("4_changelist_number_")[1]).split(".txt")[0])
			break
				
	return BuildDir( str(changeListNumber), str(buildNumber), date )
	
def createBuildsArray( location ):
	
	array = []
	if os.path.exists(location):
		dirs =  os.listdir(location)
		for dir in dirs:
			#skipping @eaDir directory in linux
			if dir == "@eaDir":
				continue
			
			if os.path.isdir(os.path.join(location,dir)):
				array.append(createBuildDir(location, dir))

	array = sorted(array)
 
	return array

