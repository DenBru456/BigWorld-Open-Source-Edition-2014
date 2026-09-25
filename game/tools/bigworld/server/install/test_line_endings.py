#!/usr/bin/env python
"""
Checks for text files with non-native line endings below the named target
directories, or $MF_ROOT/bigworld/tools/server and
$MF_ROOT/bigworld/tools/bwlockd if none are given.

Return value is the number of files found to contain non-native lines
"""

import optparse
import os
import re
import sys

PATTERN = r"\.(sh|py|conf|spec|logrotate|xml)$"

MF_ROOT = os.path.abspath( os.path.join(
	os.path.dirname( os.path.abspath( __file__ ) ), "../../../../" ) )

SRC_DIRS = [ os.path.join( MF_ROOT, "bigworld/tools/server" ),
	os.path.join( MF_ROOT, "bigworld/tools/bwlockd" ) ]

def getPath( fullPath ):
	return fullPath.split( MF_ROOT )[ -1 ][ 1: ]

class EOLChecker( object ):
	def __init__( self, regularExpression, shouldFix, quiet ):
		self.totalFiles = 0
		self.badFiles = 0
		self.dosFiles = 0
		self.macFiles = 0
		self.regularExpression = re.compile( regularExpression )
		self.shouldFix = shouldFix
		self.quiet = quiet

	def walk( self, dir ):
		if not self.quiet:
			print "Checking files from '%s'" % ( os.path.abspath( dir ), )
		for root, dirs, files in os.walk( dir ):
			try:
				dirs.remove( ".svn" )
			except ValueError:
				pass
			try:
				dirs.remove( "CVS" )
			except ValueError:
				pass

			for file in files:
				if not self.regularExpression.search( file ):
					continue
				fullFileName = os.path.join( os.path.abspath( root ), file )
				try:
					self.badFiles += self.process( fullFileName )
				except KeyboardInterrupt:
					raise
				except IOError, e:
					self.badFiles += 1
					print >> sys.stderr, "Failed to open '%s': %s" \
						% ( getPath( fullFileName ), e )

	def process( self, fileName ):
		"""
		Check that the line-ending style for this file is native, and
		potentially fix it

		Returns 1 if non-native line ending is found, 0 otherwise

		Will raise an exception if the file cannot be opened or read
		"""
		try:
			srcFile = open( fileName, "rb" )
		except IOError, e:
			raise

		self.totalFiles += 1
		line = srcFile.readline()
		srcFile.close()

		# Empty files don't matter
		if not len( line ):
			return 0

		# DOS-style line endings
		if line.endswith( "\r\n" ):
			self.badFiles += 1
			self.dosFiles += 1
			if not self.quiet:
				print "Found DOS line-endings in '%s'" % ( getPath( fileName ) )
			if self.shouldFix:
				if os.system( "dos2unix '%s' >/dev/null 2>&1" % fileName ):
					print >> sys.stderr, "Failed to convert '%s'" \
						% ( getPath( fileName ) )
					self.dosFiles -= 1
		# UNIX-style line endings
		elif line.endswith( "\n" ):
			return 0
		# MacOS-style line endings assumed
		else:
			self.badFiles += 1
			self.macFiles += 1
			if not self.quiet:
				print "Found MacOS line-endings in '%s'" \
					% ( getPath( fileName ) )
			if self.shouldFix:
				if os.system( "mac2unix '%s' >/dev/null 2>&1" % fileName ):
					print >> sys.stderr, "Failed to convert '%s'" \
						% ( getPath( fileName ) )
					self.macFiles -= 1

		return 1

def main():
	parser = optparse.OptionParser( description=globals()['__doc__'],
		usage = "%prog [options] [target directories...]" )
	parser.add_option( "-m", "--match", dest="pattern", default=PATTERN,
		help = "Regular expression matching file names to check" )
	# -c/--convert is the older option name
	parser.add_option( "-f", "--fix", "-c", "--convert", 
		action = "store_true", dest="fix",
		help = "Convert any suspect files using 'dos2unix'/'max2unix'" )
	parser.add_option( "-q", "--quiet", action = "store_true", dest="quiet",
		help = "Don't output list of suspect files" )
	# -v/--verbose is legacy interface, now that's the default
	parser.add_option( "-v", "--verbose", action = "store_false", dest="quiet",
		help = "Output list of suspect files (default)" )
	(options, args) = parser.parse_args( sys.argv[1:] )

	if options.fix:
		if os.system( "which dos2unix >/dev/null 2>&1" ):
			print >> sys.stderr, \
				"ERROR: Unable to locate 'dos2unix' for conversion."
			sys.exit( -1 )

		if os.system( "which mac2unix >/dev/null 2>&1" ):
			print >> sys.stderr, \
				"ERROR: Unable to locate 'mac2unix' for conversion."
			sys.exit( -1 )

	if len( args ) == 0:
		args = SRC_DIRS

	visitor = EOLChecker( regularExpression = options.pattern,
		shouldFix = options.fix,
		quiet = options.quiet )

	for dir in args:
		visitor.walk( dir )

	if visitor.totalFiles == 0:
		print "WARNING: No files processed"
	elif visitor.badFiles == 0:
		print "All files appear to have correct line endings"
	else:
		print "Found %d file(s) with suspicious line endings" \
			% ( visitor.badFiles, )

	if options.fix and visitor.dosFiles > 0:
		print "Successfully converted %d dos line ending file(s)." \
			% ( visitor.dosFiles, )

	if options.fix and visitor.macFiles > 0:
		print "Successfully converted %d mac line ending file(s)." \
			% ( visitor.macFiles, )


	if options.fix:
		return visitor.badFiles - ( visitor.dosFiles + visitor.macFiles )
	else:
		return visitor.badFiles

if __name__ == "__main__":
	sys.exit( main() )
