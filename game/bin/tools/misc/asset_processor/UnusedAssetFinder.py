from LogFile import errorLog
from FileUtils import fullName
from FileUtils import extension
from FileUtils import stripExtension
from FileUtils import stripPath
from FileUtils import extractSectionsByName
import AssetDatabase

#------------------------------------------------------------------------------
# Any Individual Asset Processor must have
#
# a list of extensions that the processor applies to
# a process( dbEntry ) method
#
# the process method returns true iff the file was updated.
#------------------------------------------------------------------------------

class UnusedAssetFinder:
	def __init__( self ):
		self.description = "Unused Asset Finder"
		#This list finds some FD specific assets
		#self.ignoreList = ["flora",]
		
	def appliesTo( self ):
		return ("chunk","xml","tga","bmp","jpg","dds","png","texanim","gui","py","model")

	def process( self, dbEntry ):
		"""Note that removing things from the database ensures that we will
		not be deleting it."""
		
		textures = ("tga","bmp","jpg","dds","png","texanim")
		# we shouldn't delete chunk files or anything in them
		if extension( dbEntry.name ) == "chunk":
			AssetDatabase.fileDatabase.remove( dbEntry.name )
			
		# we shouldn't delete xml files for the time being
		elif extension( dbEntry.name ) == "xml":
			AssetDatabase.fileDatabase.remove( dbEntry.name )
			
		# we shouldn't delete gui files
		elif extension( dbEntry.name ) == "gui":
			AssetDatabase.fileDatabase.remove( dbEntry.name )
			
		# we shouldn't delete script files
		elif extension( dbEntry.name ) == "py":
			AssetDatabase.fileDatabase.remove( dbEntry.name )
			
		# texture special conditions
		elif extension( dbEntry.name ) in textures:
			if dbEntry.name.find("speedtree") != -1:
				AssetDatabase.fileDatabase.remove( dbEntry.name )
			elif dbEntry.name.find("thumbnail") != -1:
				AssetDatabase.fileDatabase.remove( dbEntry.name )
			elif extension( dbEntry.name ) == "dds":
				if not len( dbEntry.usedBys ):
					AssetDatabase.fileDatabase.remove( dbEntry.name )
					
		# hack to remove model entries
		elif extension( dbEntry.name ) == "model":
			for usedBy in dbEntry.usedBys:
				if usedBy.name == "killme":
					AssetDatabase.fileDatabase.remove( dbEntry.name )
				
		return True
		