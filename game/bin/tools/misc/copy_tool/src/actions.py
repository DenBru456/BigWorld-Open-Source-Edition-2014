import os
import sys
import shutil
import stat
from log import *
from revision_control import *
import subprocess

DELETE_ACTION = "DeleteAction"
COPY_ACTION = "CopyAction"

def fixPath( path ):
	return path.replace("\\", "/")
	
class SourcePath:
	def __init__( self, path, description ):
		self.path = fixPath( path )
		self.description = description

class BaseAction:
	def __init__( self, file, destPath ):
		self._file = fixPath( file )
		self._destPath = fixPath( destPath )
	
	def __eq__( self, other ):
		if other == None:
			return False
		return self._file == other._file and \
				self.returnActionType() == other.returnActionType() and \
				self._destPath == other._destPath
	
	def __ne__( self, other ):
		return not ( self == other )
		
	def __lt__ (self, other): 
		return self._file < other._file
		
	def getFile( self ):
		return self._file

	def description( self ):
		return self._text
		
		
class DeleteAction( BaseAction ):
	def __init__( self, file, destPath):
		BaseAction.__init__( self, file, destPath )
		self._text = "delete " + self._file

	def returnActionType( self ):
		return DELETE_ACTION
		
	def execute( self, printer ):
		printer.message("Deleting " + self._file)
		os.remove(os.path.join(self._destPath, self._file))
		
class CopyAction( BaseAction ):			
	def __init__( self , file, destPath, sourcePath):
		BaseAction.__init__( self, file, destPath )
		self._source = sourcePath.path
		self._text = "copy " + self._file + " from " + sourcePath.description

	def returnActionType( self ):
		return COPY_ACTION
	
	def execute( self, printer ):
		
		def copy (newFile, originalFile, printer ) :
		
			def rmtreeErr(func, path, exc_info):
				if os.access(path, os.F_OK) and not os.access(path, os.W_OK):
					os.chmod(path, stat.S_IWUSR)
					func(path)
		
			if not os.path.exists(newFile):
				printer.warning( "couldn't find: " + newFile )
				return False					
			if os.path.isdir(newFile):
				if os.path.exists(originalFile):
					printer.message( "remove dir " + originalFile )
					shutil.rmtree( originalFile, False, rmtreeErr )
				printer.message( "copy dir from " + newFile + " to " + originalFile )
				#bug fix for python 2.4
				if not os.path.exists(os.path.dirname(originalFile)):
					os.makedirs(os.path.dirname(originalFile))
					
				shutil.copytree(newFile, originalFile)
			else:
				if os.path.exists(originalFile):
					if os.access(originalFile, os.F_OK) and not os.access(originalFile, os.W_OK):
						os.chmod(originalFile, stat.S_IWUSR)
					printer.message( "remove file " + originalFile )
					os.unlink( originalFile )
				#bug fix for python 2.4
				if not os.path.exists(os.path.dirname(originalFile)):
					os.makedirs(os.path.dirname(originalFile))
				printer.message( "copy file from " + newFile + " to " + originalFile )
				shutil.copy( newFile, originalFile )
			
		newFile = os.path.join(self._source, self._file)
		originalFile = os.path.join( self._destPath, self._file)
		copy(newFile, originalFile, printer )
		
		return True
	
class ActionList:
	def __init__( self ):
		self.actionList = []
		
	def append( self, obj ):
		self.actionList.append(obj)
		self.actionList = sorted(self.actionList)
	
	def getActionForFile( self, file ):
		return next((x for x in self.actionList if x.getFile() == file), None)
	
	def isFileInList( self, file ):
		return self.getActionForFile(file) != None
	
	def isActionInList( self, action ):
		return (next((x for x in self.actionList if x == action), None) != None)
						
	def deleteByIndex( self, index ):
		del self.actionList[index]
					
	def execute( self, printer ):
		for a in self.actionList:
			a.execute( printer = printer )		
		printer.message( "Done." )
		return True
	
	def removeActions( self, predicate ):
		self.actionList = [x for x in self.actionList if not predicate(x)]
	
	def removeDeleteActions( self ):
		self.removeActions( lambda x: x.returnActionType() == DELETE_ACTION )
							
