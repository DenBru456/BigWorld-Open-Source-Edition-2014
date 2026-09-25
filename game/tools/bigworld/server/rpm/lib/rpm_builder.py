from lib.package_list_parser import PackageListParser
from lib.macro_expander import MacroExpander
from lib.version_file_parser import VersionFileParser
from lib.spec_template import SpecTemplate
import lib.svn_assistant as SVNAssistant

import bwsetup
bwsetup.addPath( "../.." )
import pycommon.p4_version as P4Version

import glob
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import datetime

bwBuildMakeDir = os.path.abspath( os.path.join(
	os.path.dirname( __file__ ), "../../../../../../programming/bigworld/build/make" ) )

sys.path.append( bwBuildMakeDir )
import platform_info

PLATFORM_CONFIG = platform_info.findPlatformName()
if not PLATFORM_CONFIG:
	print "Failed to discover platform config."
	sys.exit( 1 )

CLEANUP_TMP_FILE = "cleanup.tmp"
BINARY_RPM_TMP_FILE = "binary_rpm.tmp"

VERSION_FILE_PATH = "programming/bigworld/lib/cstdmf/bwversion.hpp"

log = logging.getLogger( 'rpm_builder' )


def generatePlatformAlternatives():
	"""This function generates a set of appropriate platform alternatives to be
	used when attempting to find the name of the RPM build files to use. They
	will be returned as an iterable in decreasing order of priority."""

	alternatives = [ PLATFORM_CONFIG, ]

	if PLATFORM_CONFIG.startswith( "el" ):
		alternatives.append( PLATFORM_CONFIG.replace( "el", "centos" ) )

	# If the platform is 'rhel5' / 'centos5', use the existing unlabeled files
	if alternatives[ -1 ] in ("centos5", "centos6", "el5", "el6"):
		alternatives.append( "" )

	return alternatives


class RPMBuilder( object ):
	"""
	This class builds an RPM from a RPM spec file template, and a file list. It
	gathers the files specified by the file list, and creates a temporary build
	root directory, populated by those specified files. It then creates the RPM
	spec file from the template, and runs rpmbuild to create the RPM file,
	which is then copied to the given output directory.

	Once an object is initialised, use the build() method to actually trigger
	the build.
	"""

	def __init__( self, bwRoot, packageDir, isIndie = False,
				  bwInstallDir = None, createPackageVersion = False ):
		"""
		@param bwRoot 		The top-level directory for the BigWorld source
							distribution.
		@param packageDir 	The package name. This must be a directory under
							the current working directory, and it must also
							contain the file list (expected to be
							<PACKAGENAME>.lst) and template specification file
							(expected to be <PACKAGENAME>_template.spec).
		"""
		self.buildWarnings = []
		self.bwRoot = bwRoot
		self.packageDir = packageDir
		self.isIndieBuild = isIndie
		self.bwInstallDir = bwInstallDir
		platformAlternatives = generatePlatformAlternatives()

		self.specTemplate = None
		for alternative in platformAlternatives:
			altStr = "_%s" % alternative
			if not alternative:
				altStr = alternative
			baseFile = "%s_template%s.spec" % (packageDir, altStr)
			specTemplateFilePath = os.path.join( packageDir, baseFile )

			try:
				self.specTemplate = SpecTemplate( specTemplateFilePath )
				break
			except IOError, ioe:
				log.warn( "Failed to load spec file '%s'",
					specTemplateFilePath )
				self.specTemplate = None

		if not self.specTemplate:
			log.critical( "Unable to find any valid spec file for %s",
				packageDir )
			sys.exit( 1 )

		self.macroExpander = self.specTemplate.macroExpander()

		self.packageListParser = None
		for alternative in platformAlternatives:
			altStr = "_%s" % alternative
			if not alternative:
				altStr = alternative
			baseFile = "%s%s.lst" % (packageDir, altStr)

			fileListPath = os.path.join( packageDir, baseFile )

			try:
				self.packageListParser = PackageListParser( fileListPath )
				break
			except IOError:
				log.warn( "Failed to load lst file '%s'", fileListPath )
				self.packageListParser = None

		if not self.packageListParser:
			log.critical( "Unable to find any valid lst file for %s",
				packageDir )
			sys.exit( 1 )

		versionFilePath = os.path.join( bwRoot, VERSION_FILE_PATH )
		version = VersionFileParser( versionFilePath )

		versionStrings = [version.major, version.minor]

		versionString = ".".join( versionStrings )
		self.macroExpander['bw_version'] = versionString
		self.macroExpander['bw_patch'] = version.patch

		repositoryType = ""
		revisionNumber = SVNAssistant.latestRevision( bwRoot )
		if int(revisionNumber):
			repositoryType = "SVN"
		else:
			log.info( "Loading Perforce revision information." )
			p4VersionInfo = None
			try:
				p4VersionInfo = P4Version.loadVersionInfo()
			except Exception, err:
				self.buildWarnings.append( err )

			if p4VersionInfo:
				revisionNumber = p4VersionInfo[ 'revisionNumber' ]
				repositoryType = "Perforce"
			else:
				revisionNumber = "0"

		revisionString = "r" + revisionNumber
		self.macroExpander['bw_revision'] = revisionString

		arch = MacroExpander.rpmExpand( '%{_arch}' )
		self.macroExpander['platform_config'] = PLATFORM_CONFIG

		# CentOS5 does not define %{dist}
		el5Platforms = ["centos5", "rhel5", "el5"]
		if PLATFORM_CONFIG in el5Platforms:
			self.macroExpander['dist'] = ".el5"

		log.info( "Version: %s.%s (%s)", versionString, version.patch, arch )
		if revisionNumber:
			log.info( "Revision: %s", revisionNumber )

		rpmsDir = MacroExpander.rpmExpand( '%{_rpmdir}' )
		name = self.macroExpander.expand( '%{name}' )
		dist = self.macroExpander.expand( '%{dist}' )

		versionFileName = packageDir + "_version_" + \
			datetime.datetime.now().strftime("%Y%m%d_%H%M") + "_" + \
			str( os.getpid() )
		self.macroExpander['bigworld_tmp_version_file'] = \
			os.path.join( tempfile.gettempdir(), versionFileName )

		# The expected output path from rpmbuild, unfortunately, this can't be
		# changed other than setting .rpmmacros.
		self.outputPathPrefix = os.path.join( rpmsDir, arch, "%(name)s" %
				dict( name = name ) )

		self.outputPathSuffix = "-%(version)s.%(patch)s-%(patch)s." \
			"%(revision)s%(dist)s.%(arch)s.rpm" % \
				dict( version = versionString,
					patch = version.patch,
					revision = revisionString,
					arch = arch,
					dist = dist )

		if createPackageVersion:
			self._generatePackageVersionFile ( packageDir, versionString,
			 	version.patch, repositoryType, revisionNumber )


	def _rpmFiles( self ):
		return self.packageListParser.fileList( self.bwRoot, 
			self.macroExpander, self.bwInstallDir )

	def _populateBuildRoot( self, buildRoot ):
		for file in self._rpmFiles():
			file.apply( buildRoot, self.macroExpander,
				   self.packageListParser.filters.get( file.destination ) )

	def _createBuildRoot( self ):
		return tempfile.mkdtemp( "", "rpm_build_" + self.packageDir + "_", 
			os.environ.get( "TMPDIR", "/tmp" ) )


	def _tearDownBuildRoot( self, buildRoot ):
		shutil.rmtree( buildRoot, ignore_errors=True )


	def _createSpecFile( self, buildRoot ):
		specFilePath = os.path.join( self.packageDir, 
			self.packageDir + ".spec" )

		self.specTemplate.writeSpecFile( specFilePath, buildRoot, 
			self._rpmFiles(), self.macroExpander )

		return specFilePath


	@staticmethod
	def _createRPM( specFilePath, buildRoot ):
		"""
		Use the rpmbuild command to build the RPM from a RPM spec file. This
		will output to a directory of rpmbuild's choosing.
		"""
		cmd = ['rpmbuild', '-bb', '-v', '--buildroot', buildRoot, specFilePath]

		try:
			pipe = subprocess.Popen( cmd, 
				stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
		except OSError:
			print "Failed to execute %s. Make sure rpm-build is installed." % \
				cmd[0]
			sys.exit( 1 )

		output = ''

		# translate each output line into a log entry
		while pipe.poll() is None:
			output += pipe.stdout.read( 32 )
			lines = output.split( "\n" )
			if len( lines ) > 1:
				for line in lines[:-1]:
					log.info( "rpmbuild: %s", line )
				output = lines[-1]

		returnCode = pipe.wait()

		if not os.WIFEXITED( returnCode ) or os.WEXITSTATUS( returnCode ) != 0:
			raise ValueError, "rpmbuild returned code: %d" % returnCode



	def _generateDestinationForRPM( self, potentialRPM ):

		rpmSuffix = potentialRPM[ len( self.outputPathPrefix ): ]
		subPackage = rpmSuffix[ :-len( self.outputPathSuffix ) ]

		nameExt = ""
		if self.isIndieBuild:
			nameExt = "-indie"

		revisionString = self.macroExpander.expand( '%{bw_revision}' )

		if revisionString != "r0":
			formattedRevision = ".%s" % revisionString
		else:
			formattedRevision = ""

		name = self.macroExpander.expand( '%{name}' )
		versionString = self.macroExpander.expand( '%{bw_version}' )
		patchVersion = self.macroExpander.expand( '%{bw_patch}' )
		arch = self.macroExpander.expand( '%{_arch}' )
		dist = self.macroExpander.expand( '%{dist}' )

		destFile = "%(name)s%(subPackage)s%(name_ext)s-%(version)s.%(patch)s%(revision)s%(dist)s.%(arch)s.rpm" % \
				dict( name = name,
					subPackage = subPackage,
					name_ext = nameExt,
					version = versionString,
					patch = patchVersion,
					revision = formattedRevision,
					dist = dist,
					arch = arch )

		return destFile


	def _generatePackageVersionFile( self, packageDir, versionString, patch,
								 repositoryType, revisionNumber ):
		"""
		Generate a text-format version file in the specified package directory.

		@param versionString	Base version number (major + minor)
		@param patch			Version patch number
		@param revisionNumber	Local revision of bwRoot dir
		"""
		versionFile = self.macroExpander.expand( '%{bigworld_tmp_version_file}' )

		try:
			fp = open( versionFile, "w" );

			fp.write( "Package: " + packageDir + "\n" )
			fp.write( "Version: " + versionString + "\n" )
			fp.write( "Patch: " + str( patch ) + "\n" )
			fp.write( "RepositoryType: " + str( repositoryType ) + "\n" )
			fp.write( "Revision: " + str( revisionNumber ) + "\n" )
			fp.write( "" )
			fp.close()
		except Exception, e:
			log.info( "Error writing to version file '%s': %s", versionFile, str( e ) )
			raise e


	def build( self, outputDir, tearDownRoot = True, deleteTempRPM = False ):
		"""
		Build an RPM.

		@param outputDir 	The output directory where the RPM will be placed.
		"""

		buildRoot = self._createBuildRoot()
		specFilePath = None

		result = True

		try:
			log.info( "Populating build root" )
			self._populateBuildRoot( buildRoot )

			log.info( "Creating spec file" )
			specFilePath = self._createSpecFile( buildRoot )

			if not tearDownRoot:
				backupPath = "/tmp/" + os.path.basename( specFilePath )
				log.info( "Backing up spec file %s to %s" %
						( specFilePath, backupPath ) )
				shutil.copyfile( specFilePath, backupPath )

			log.info( "Creating RPM" )
			self._createRPM( specFilePath, buildRoot )


			outputRpmGlob = self.outputPathPrefix + "*"
			matchingRPMs = glob.glob( outputRpmGlob )

			if len( matchingRPMs ) == 0:
				raise ValueError, \
					"Could not find built RPM at %s" % outputRpmGlob

			for potentialRPM in matchingRPMs:
				destFileName = self._generateDestinationForRPM( potentialRPM )
				destFilePath = os.path.join( outputDir, destFileName )

				if deleteTempRPM:
					shutil.move( potentialRPM, destFilePath )
					log.info( "Moved %s to %s", potentialRPM, outputDir )

				else:
					shutil.copy( potentialRPM, destFilePath )
					log.info( "Copied %s to %s", potentialRPM, outputDir )

			result = True
		except ValueError, e:
			print "Build failure:", str( e )
			result = False

		if tearDownRoot:
			log.info( "Tearing down build root" )
			self._tearDownBuildRoot( buildRoot )
			if not specFilePath is None:
				os.remove( specFilePath )
		else:
			log.info( "Not tearing down %s" % buildRoot )


		# Reiterate non-interrupting warnings to the user at the end
		if len( self.buildWarnings ):
			log.warning( "-- Outstanding warnings from rpmbuild --" )
			[ log.warning( warning ) for warning in self.buildWarnings ]

		return result


# rpm_builder.py
