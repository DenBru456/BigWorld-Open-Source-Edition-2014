"""
Module for package file objects.
"""

import os
import shutil

import logging
log = logging.getLogger( 'rpm_builder' )

def _makeDestDir( dest ):
	destDir = os.path.dirname( dest )
	if not os.path.exists( destDir ):
		os.makedirs( destDir )


def _createLink( source, dest ):
	_makeDestDir( dest )
	os.symlink( source, dest )


def _copyFile( source, dest ):
	"""
	This method wraps shutil.copyfile by creating the intended containing
	directory if it does not already exist.

	@param source 	The source path.
	@param dest		The destination path.
	"""
	_makeDestDir( dest )

	if os.path.isfile( source ):
		shutil.copyfile( source, dest )
	elif os.path.isdir( source ):
		if not os.path.exists( dest ):
			os.makedirs( dest )


class PackageFile( object ):
	"""
	Generic file.
	"""
	def __init__( self, lineNum, subPackage, source, destination, mode, owner, group ):
		self.lineNum = lineNum
		self.source = source
		self.destination = destination
		self.mode = mode
		self.owner = owner
		self.group = group
		self.subPackage = subPackage

	def clone( self, newClass=None ):
		"""
		Return a copy of this PackageFile, possibly as a different package file
		type.
		"""
		assert( self.__class__.__name__ != "NewDirPackageFile" )
		if newClass == None:
			newClass = self.__class__

		return newClass( self.lineNum, self.subPackage, self.source, self.destination, 
			self.mode, self.owner, self.group )


	def specFileEntry( self ):
		if " " in self.destination:
			log.warning("The destination file %s contains spaces, consider " \
				"renaming this file." % self.destination)
		return "%%attr( %(mode)s, %(owner)s, %(group)s ) \"%(destination)s\"" % \
			dict( mode=self.mode, owner=self.owner, group=self.group,
				destination=self.destination )

	def apply( self, buildRoot, macroExpander, filters ):
		destinationPath = buildRoot + \
			macroExpander.expand( self.destination )
		log.debug( "copying %s to %s", self.source, destinationPath )

		if not os.path.exists( self.source ):
			log.error( "File not found (from line %d): %s. Aborting build.", 
				self.lineNum, self.source )
			raise ValueError( "At least one of the source files is missing" )

		_copyFile( self.source, destinationPath )

		if not filters.run( destinationPath, macroExpander ):
			raise ValueError( "Filtering failed" )

	def isCopy( self ):
		return True


class LinkPackageFile( PackageFile ):
	def apply( self, buildRoot, macroExpander, filters ):
		destinationPath = buildRoot + macroExpander.expand( self.destination )
		log.debug( "linking %s to %s", self.source, destinationPath )

		sourcePath = macroExpander.expand( self.source )

		_createLink( sourcePath, destinationPath )

	def isCopy( self ):
		return False


class ConfigPackageFile( PackageFile ):
	"""
	Configuration file.
	"""
	def __init__( self, lineNum, subPackage, source, destination, mode, owner, group ):
		PackageFile.__init__( self, lineNum, subPackage, source, destination, mode, owner, group )


	def specFileEntry( self ):
		return "%config " + PackageFile.specFileEntry( self )


class ConfigNoReplacePackageFile( PackageFile ):
	"""
	Configuration file.
	"""
	def __init__( self, lineNum, subPackage, source, destination, mode, owner, group ):
		PackageFile.__init__( self, lineNum, subPackage, source, destination, mode, owner, group )


	def specFileEntry( self ):
		return "%config(noreplace) " + PackageFile.specFileEntry( self )


class DirPackageFile( PackageFile ):
	"""
	Directory file.
	"""
	def __init__( self, lineNum, subPackage, source, destination, mode, owner, group ):
		PackageFile.__init__( self, lineNum, subPackage, source, destination, mode, owner, group )
		self._adjustMode()


	def _adjustMode( self ):

		# If a user class has read permissions, make sure it also has execute
		# permissions.
		# Need to do it for user, group and all user classes.

		modeNum = int( self.mode, 8 )

		MODE_READ_BIT = 0x4 
		MODE_EXECUTE_BIT = 0x1
		BITS_PER_OCTAL_DIGIT = 3
		for i in xrange( 3 ):
			if MODE_READ_BIT << (i * BITS_PER_OCTAL_DIGIT) & modeNum:
				modeNum |= MODE_EXECUTE_BIT << (i * BITS_PER_OCTAL_DIGIT)

		self.mode = oct( modeNum )


	def specFileEntry( self ):
		return "%dir " + PackageFile.specFileEntry( self )


class NewDirPackageFile( DirPackageFile ):
	def apply( self, buildRoot, macroExpander, filters ):
		destDir = buildRoot + macroExpander.expand( self.destination )
		if not os.path.exists( destDir ):
			os.makedirs( destDir )

	def isCopy( self ):
		return False

# package_file.py

