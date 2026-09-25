"""
Module for parsing a package list file.

Package List File Syntax
------------------------

Each line in a package list file is either blank, a comment prefixed by #, or a
command. Commands are given using the following syntax:
    <command> <arg string>

Available commands:

add: Add a file. The arg string is a comma-separated list of the following
parameters:
  * source relative path from MF_ROOT (can contain macros)
  * destination absolute path (can contain macros)
  * file mode
  * file owner (optional, defaults to root)
  * file group (optional, defaults to root)

addConfig: Same as add, but causes the file to be marked in the RPM spec file
as a configuration file.

excludePathPatterns: Specify an exclusion pattern for the source file.
The arg string is a regular expression against which the source path for all
files specified using add or addConfig are searched against, a match means that
the file is excluded.

excludeDestPathPatterns: Specify an exclusion pattern. The arg string is a
regular expression against which the destination path for all files specified
using add or addConfig are searched against, a match means that the file is
excluded.


Typical Usage
-------------

from macro_expander import MacroExpander
parser = PackageListParser( path )
macroExpander = MacroExpander()

macroExpander['platform_config'] = ...
...

for packageFile in parser.fileList( bwRoot, macroExpander ):
    # do something with packageFile, which is a PackageFile object

    # on error, you can inform the user of where the error is via
    # packageFile.lineNum



"""


from macro_expander import MacroExpander
from package_file import PackageFile, ConfigPackageFile, \
		ConfigNoReplacePackageFile, DirPackageFile, NewDirPackageFile, \
		LinkPackageFile

import logging
import os
import re

log = logging.getLogger( 'package_list_parser' )

from filters import Filters

def parseCommand( d, name ):
	"""
	Decorator for parse commands.
	"""
	def decorated( fn ):
		d[name] = fn
		return fn
	return decorated

class PackageListParser( object ):
	"""
	Class to parse a package list. 
	"""

	PARSE_COMMANDS = {}

	def __init__( self, packageListPath ):
		"""
		Constructor.

		@param packageListPath 		Path to the package list file.
		"""

		self.excludeSrcPathPatterns = []
		self.excludeDestPathPatterns = []
		self.packageFiles = []
		self.filters = Filters()

		lines = open( packageListPath, "r" ).xreadlines()
		self._parseCommands( lines )


	@parseCommand( PARSE_COMMANDS, "add" )
	def _parseAdd( self, line, lineNum, subPackage,
			packageFileClass = PackageFile, hasSource = True ):
		components = line.split( "," )

		if hasSource:
			source = components.pop( 0 )
		else:
			source = None

		if len( components ) < 2:
			raise ValueError, "Invalid number of components for add command"

		destination = components.pop( 0 )
	   	mode = components.pop( 0 )

		owner = group = 'root'

		if len( components ) >= 2:
			owner = components.pop( 0 )
		   	group = components.pop( 0 )

		self.packageFiles.append(
			packageFileClass( lineNum, subPackage, source, destination,
				mode, owner, group ) )


	@parseCommand( PARSE_COMMANDS, "addConfig" )
	def _parseAddConfig( self, line, lineNum, subPackage ):
		self._parseAdd( line, lineNum, subPackage,
			packageFileClass = ConfigPackageFile )


	@parseCommand( PARSE_COMMANDS, "addConfig(noreplace)" )
	def _parseAddConfigNoReplace( self, line, lineNum, subPackage ):
		self._parseAdd( line, lineNum, subPackage,
			packageFileClass = ConfigNoReplacePackageFile )


	@parseCommand( PARSE_COMMANDS, "excludePathPatterns" )
	def _parseExcludePathPatterns( self, line, lineNum, subPackage ):
		pattern = re.compile( line )
		self.excludeSrcPathPatterns.append( pattern )


	@parseCommand( PARSE_COMMANDS, "excludeDestPathPatterns" )
	def _parseExcludeDestPathPatterns( self, line, lineNum, subPackage ):
		pattern = re.compile( line )
		self.excludeDestPathPatterns.append( pattern )


	@parseCommand( PARSE_COMMANDS, "link" )
	def _parseLink( self, line, lineNum, subPackage ):
		self._parseAdd( line, lineNum, subPackage,
			packageFileClass = LinkPackageFile )


	@parseCommand( PARSE_COMMANDS, "dir" )
	def _parseDir( self, line, lineNum, subPackage ):
		self._parseAdd( line, lineNum, subPackage,
			packageFileClass = NewDirPackageFile, hasSource = False )


	@parseCommand( PARSE_COMMANDS, "filter" )
	def _filterFile( self, line, lineNum, subPackage ):
		self.filters.add( line )


	def _parseCommands( self, lines ):
		"""
		Parse the commands in the given lines.
		"""
		for i, line in enumerate( lines ):
			lineNum = i + 1
			if line.strip() == "" or line.strip().startswith( '#' ):
				continue

			tokens = line.split( " ", 1 )

			if len( tokens ) < 2:
				raise ValueError, \
					"Error at line %d: not enough tokens" % lineNum

			cmdStr, args = tokens
			cmdList = cmdStr.split( "," )
			subPackage = None

			if len( cmdList ) > 1:
				subPackage = cmdList[ 1 ]

			cmd = cmdList[ 0 ]

			if cmd in PackageListParser.PARSE_COMMANDS.keys():
				parseCommand = PackageListParser.PARSE_COMMANDS[ cmd ]
				try:
					parseCommand( self, args.strip(), lineNum, subPackage )
				except Exception, e:
					raise ValueError, "Error at line %d: %s" % (lineNum, e)
			else:
				raise ValueError, "Invalid line %d, unknown command %r" % cmd


	def _shouldExclude( self, path ):
		if path is not None:
			for pattern in self.excludeSrcPathPatterns:
				if pattern.search( path ):
					return True

		return False


	def _shouldExcludeDestination( self, destPath ):
		if destPath is not None:
			for pattern in self.excludeDestPathPatterns:
				if pattern.search( destPath ):
					return True

		return False


	def fileList( self, bwRoot, macroExpander, bwInstallDir = None ):
		"""
		Return a generator for PackageFile objects as specified by the package
		list file.

		Each PackageFile object represents a single file, with absolute
		macro-expanded source path. The destination path is kept as
		un-expanded.

		The destination paths of the PackageFiles generated from this function
		are guaranteed to be unique, if there are multiple lines specifying the
		same destination in the package list file, the first one takes
		precedence, and its attributes are applied. 

		@param bwRoot 			The top level directory for the source relative
								paths.
		@param macroExpander 	A MacroExpander object able to expand macros in
								the source and destination paths.

		"""
		dests = set()

		for packageFile in self._rawFileList( bwRoot, macroExpander, bwInstallDir ):
			if self._shouldExclude( packageFile.source ):
				continue
			expandedDestination = macroExpander.expand( 
				packageFile.destination )

			if expandedDestination in dests or \
				self._shouldExcludeDestination( expandedDestination ):
				continue

			dests.add( expandedDestination )
			yield packageFile

	def _rawFileList( self, bwRoot, macroExpander, bwInstallDir = None ):
		"""
		Return the raw file list.
		"""
		for packageFile in self.packageFiles:
			#Prioritise looking for files in BW_INSTALL_DIR if it is defined
			useInstallDir = False
			sources = []
			if bwInstallDir:
				source = os.path.abspath( os.path.join( bwInstallDir, 
					macroExpander.expand( packageFile.source ) ) )

				if os.path.exists( source ):
					sources.append( source )

			source = os.path.abspath( os.path.join( bwRoot, 
					macroExpander.expand( packageFile.source ) ) )
			sources.append( source )

			# TODO: Move this functionality into PackageFile
			if not packageFile.isCopy():
				yield packageFile
			elif os.path.isdir( sources[0] ):
				relativeFilePaths = []
				for source in sources:
					# Include an entry for the directory itself.
					dirPackageFile = packageFile.clone( DirPackageFile )
					dirPackageFile.source = source
					yield dirPackageFile

					# The source file is a directory, walk through it and yield
					# each file found.
					for path, dirs, files in os.walk( source ):
						for filePath in files:
							fullSourcePath = os.path.join( path, filePath )
							relativeFilePath = fullSourcePath[len( source ):]
							if relativeFilePath in relativeFilePaths:
								continue
							relativeFilePaths.append( relativeFilePath )
							childPackageFile = packageFile.clone()
							childPackageFile.source = fullSourcePath
							childPackageFile.destination = \
								packageFile.destination + relativeFilePath
							yield childPackageFile

						for dirPath in dirs:
							fullSourcePath = os.path.join( path, dirPath )
							relativeDirPath = fullSourcePath[len( source ):]

							childPackageFile = \
								packageFile.clone( DirPackageFile )
							childPackageFile.source = fullSourcePath
							childPackageFile.destination = \
								packageFile.destination + relativeDirPath
							yield childPackageFile

			elif os.path.isfile( sources[0] ) or \
					not os.path.exists( sources[0] ):
				# files and non-existent paths
				childPackageFile = packageFile.clone()
				childPackageFile.source = sources[0]
				yield childPackageFile
			else:
				# Might be a symlink, socket file or other unsupported file
				# type. Shouldn't be in MF_ROOT.
				raise ValueError, "File type not supported for %s" % sources[0]

# package_list_parser.py
