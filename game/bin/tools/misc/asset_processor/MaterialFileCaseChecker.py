import sys
x=sys.path
import AssetProcessorSystem
import ResMgr
sys.path=x
import FileUtils
from LogFile import errorLog		
import AssetDatabase
import os

from MaterialSectionProcessorBase import MaterialSectionProcessorBase

class MaterialFileCaseChecker( MaterialSectionProcessorBase ):
	'''This checks that material file names match the case saved on the disk.'''

	def __init__( self ):
		MaterialSectionProcessorBase.__init__( self )
		self.description = "File case checker"

	def appliesTo( self ):
		return ("model","visual","mfm","chunk")

	def process(self,dbEntry):
		return MaterialSectionProcessorBase.process( self, dbEntry )

	def processMaterialSection( self, sect, dbEntry ):
		success = True
		
		# Get resource paths to search for files
		resPaths = FileUtils.getResourcePaths()

		# Add bigworld/res and current directory to search paths
		resPaths.append( "" )
		resPaths.append( os.path.abspath( "../../../../bigworld/res" ) + "/" )

		# Iterate over material file names
		for dependency in dbEntry.dependencies:

			fileName = dependency.name
			foundFile = False
			
			# Search for the file in all of the search paths
			for resPath in resPaths:

				resPath = resPath.replace( "\\", "/" )
				absFileName = os.path.normpath( resPath + fileName )

				foundFile = os.path.exists( absFileName )
				if foundFile:
					(caseMatchesDisk, diskName) = \
						self.checkFileCase( absFileName )

					if not caseMatchesDisk:
						errorLog.errorMsg( "File case mismatch: " + absFileName +
							" should be " + diskName + " in " + dbEntry.name )
						success = False
					break

			# Could not find file in any search path
			if not foundFile:
				errorLog.errorMsg( "File does not exist " + fileName +
					" in " + dbEntry.name )

		return success

	def checkFileCase( self, absFileName ):
		'''Use the Windows SHParseDisplayName to get the case of the file on
		disk.
		@return (caseMatchesDisk, diskName)
		caseMatchesDisk is True if the given filename matches that on the disk.
		diskName returns the filename that was found on the disk (with correct
			case.
		'''
		import ctypes
		
		class SHITEMID( ctypes.Structure ):
			_fields_ = [ ("cb", ctypes.c_ushort),
						 ("abID", ctypes.c_char * 1 ) ]

		class ITEMIDLIST( ctypes.Structure ):
			_fields_ = [ ( "mkid", SHITEMID ) ]

		SFGAO_FILESYSTEM = ctypes.c_ulong( 0x40000000L )
		wpath = ctypes.c_wchar_p( absFileName )
		hr = ctypes.HRESULT()
		pidl = ctypes.POINTER(ITEMIDLIST)()
		sfgaoOut = ctypes.c_ulong( 0L )

		hr = ctypes.windll.shell32.SHParseDisplayName(
			wpath, 0, ctypes.byref( pidl ), SFGAO_FILESYSTEM, sfgaoOut )

		if (hr >= 0):
			wbuffer = ctypes.create_unicode_buffer( '\000' * 260 )
			ctypes.windll.shell32.SHGetPathFromIDList( pidl, wbuffer )
			ctypes.windll.shell32.ILFree( pidl )
			diskName = ctypes.string_at( wbuffer.value )
		else:
			diskName = "<Unknown disk name>"

		if diskName == absFileName:
			return (True, diskName)
		return (False, diskName)
