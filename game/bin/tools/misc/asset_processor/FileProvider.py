import os
from Queue import Queue
import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
from FileUtils import extractSectionsByName
from FileUtils import extractPath
from FileUtils import extension
from FileUtils import stripPath
from LogFile import errorLog

ignoreList = []								

# The FileProvider class simply extracts
# all files from the directory structure
# that match the given extensions
class FileProvider:
	def __init__(self,extensionList,processAllPaths = False):
		self.processAllPaths = processAllPaths
		self.extensions = extensionList
		self.ignore = ("CVS","Root","Entries","Entries.Extra","Repository", ".svn")
		self.files = Queue()
		self.folders = Queue()
		self.alreadyDone = {}
		
	def begin(self):
		self.alreadyDone = {}
		self.tagEngineResources()
		
		#get the root
		sect = ResMgr.openSection("")
		if sect == None:
			return False
		self.folders.push((sect,""))
		
		return True
		
	def next(self):
		while self.files.isEmpty():
			if self.folders.isEmpty():
				return (None,None)
				
			(folder,path) = self.folders.pop()
			self.searchFolder(folder,path)
			
		return self.files.pop()
		
	def searchFolder(self,folderSection,basePath):
		keys = folderSection.keys()
		
		if (basePath=="") and (self.processAllPaths==True):
			keys = self.removeNonPrimaryPaths(keys)
			
		for name in keys:
			name = name.replace("\\","/")
			if not name in self.ignore:
				sect = folderSection[name]				
				if self.isRelevantFile(name):
					fileName = basePath+name
					#print "FILE : ", fileName
					if sect != None:						
						if not self.alreadyDone.has_key( fileName ):
							ext = extension(fileName)							
							self.files.push((ext,fileName))
							self.alreadyDone[fileName] = True
					else:
						errorLog.errorMsg( "File error - %s is not a valid XML file" % (fileName,) )
				elif self.isFolder(sect):
					#print "FOLDER : ", basePath + sect.name + "/"
					self.folders.push((sect,basePath+sect.name+"/"))
				
	def isRelevantFile(self,name):
		if name == "":
			return False			
		ext = extension(name)
		if ext == "":
			return False					
		return ext in self.extensions			
		
	#not entirely accurate, but strips out any files
	def isFolder(self,sect):
		if sect == None:
			return False
		if "." in sect.name:
			return False						
		return True			
			
	#removes paths from mf/bigworld/res that don't need processing
	def removeNonPrimaryPaths(self,keys):
		remove = ["helpers","system","shaders"]
		ret = []
		for i in keys:
			if not i in self.remove:
				ret.append(i)
		return ret	
				
	#this function tags all of the system resources ( found in resources.xml )
	#as already done, meaning they will be ignored if found during the
	#conversion process.  the system resources have already been converted.
	def tagEngineResources(self):
		self.tagXMLResources("resources.xml")
		
		#CZ specific
		self.tagXMLResources("entities/common/resources/shieldManagerResources.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_corona.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_explosion_glare.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_glow.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_majorprojectileflare.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_moon.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_particles.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_spark_flare.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_streak.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_streak_rainbow.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_streaknosec.xml")
		self.tagXMLResources("sets/global/fx/flares/fx_sun.xml")		
		
	def tagXMLResources(self,name):
		rs = ResMgr.openSection(name)
		if rs != None:
			self.tagSection(rs)		
		
	def tagSection(self,sect):
		global ignoreList
		value = sect.asString
		value = value.replace("\\","/")
		if ".mfm" in value:			
			if not self.alreadyDone.has_key(value):
				errorLog.infoMsg( "ignoring %s" % (value,) )
				ignoreList.append(value)
				self.alreadyDone[value] = True
		elif ".visual" in value:			
			if not self.alreadyDone.has_key(value):
				errorLog.infoMsg( "ignoring %s" % (value,) )
				ignoreList.append(value)
				self.alreadyDone[value] = True
			
		for child in sect.values():
			self.tagSection(child)
												
		