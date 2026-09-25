#!/usr/bin/env python

import sys
import os
import re
import optparse
import shutil

BASE_PATH = os.path.normpath( os.path.dirname( os.path.abspath(__file__) ) )

# Where the tutorial resources are
RES_PATH = os.path.join( BASE_PATH, "res" )

SCRIPT_PATH = os.path.join( RES_PATH, "scripts", "common" )

sys.path.append( SCRIPT_PATH )

import tutorial
import chapters

# File types we ignore
EXCLUDE_PATTS = [ "\.pyc$", "~", "\.include$" ]

# ------------------------------------------------------------------------------
# Section:
# ------------------------------------------------------------------------------

class InvalidChapterError( Exception ):
	def __init__( self, chapter ):
		self.chapter = chapter

	def __str__( self ):
		return "InvalidChapterError: " + self.chapter

def stringToChapter( chapter ):
	sign = '+'

	if chapter:
		if chapter[0] in ('+', '-'):
			sign = chapter[0]
			chapter = chapter[1:]
	try:
		if sign == '-':
			return -getattr( chapters, chapter )
		else:
			return getattr( chapters, chapter )
	except AttributeError, e:
		raise InvalidChapterError( chapter )

def chapterToString( chapterNum ):
	for attr in dir( chapters ):
		if attr[0] != '_':
			if getattr( chapters, attr ) == chapterNum:
				return attr

	return '?'


# ------------------------------------------------------------------------------
# Section: Stripping logic
# ------------------------------------------------------------------------------

# The functions in this section provide the stripping functionality that allows
# a user to strip whole files and lines of text from the tutorial resources to
# give them the resources needed for a particular stage of the tutorial.

def stripXML( fname, outfile ):

	dropuntil = None

	for line in open( fname ):

		# Open include block
		m = re.search( "<!-- (\{+)([\+\-]\w+)", line )
		if m:
			lvl = len( m.group( 1 ) )
			chap = stringToChapter( m.group( 2 ) )

			if tutorial.excludes( chap ):
				dropuntil = (lvl, chap)

			continue

		# Close include block
		m = re.search( "([\+\-]\w+)(\}+) -->", line )
		if m:
			lvl = len( m.group( 2 ) )
			chap = stringToChapter( m.group( 1 ) )

			# Cancel dropping if necessary
			if dropuntil == (lvl, chap):
				dropuntil = None

			continue

		if dropuntil is None:
			outfile.write( line )

	# print "Stripped", fname


def stripPy( fname, outfile ):

	depths = []

	# Whether or not we just saw an include line
	prevInclude = False

	# Macro to give the indentation level for a line
	def depth( line ):
		m = re.match( "(\t+)", line )
		if m:
			return len( m.group( 1 ) )
		else:
			return 0

	for line in open( fname ):

		if "import tutorial" in line:
			continue

		# We support an else: for an include block, but we don't support elif:
		if depths and line.startswith( "\t" * depths[-1][0] + "else:" ):
			depths[-1] = (depths[-1][0], not depths[-1][1])
			prevInclude = True
			continue

		# Check if the line we're at closes the depth we're re-indenting for
		else:
			while depths and line.strip() and depth( line ) <= depths[-1][0]:
				depths.pop()

		# Catch lines that check the tutorial stage
		if not line.startswith( "#" ) and "tutorial.includes(" in line:

			# Figure out if we're including or not
			statement = re.sub( r".*?if (.*):.*", r"\g<1>", line )
			# statement = re.sub( "tutorial.", "", statement )

			# Make a record of it
			depths.append( (depth( line ), eval( statement )) )
			prevInclude = True
			continue

		elif line.strip():
			prevInclude = False

		# Check if we can output this line
		if (not depths or depths[-1][1]) and not prevInclude:

			# Strip as many leading tabs as we have depths
			if depths:
				line = re.sub( "\t", "", line, len( depths ) )

			outfile.write( line )

	# print "Stripped", fname


def main():

	opt = optparse.OptionParser( usage = "%prog [options] chapter_name" )
	opt.add_option( "-o", "--outdir", help = "Specify the output directory" )
	(options, args) = opt.parse_args()

	if len( args ) > 1:
		opt.error( "Wrong number of arguments" )
		return 1
	elif len( args ) == 1:
		outDir = args[0].lower()

		try:
			chapter = stringToChapter( args[0] )
		except InvalidChapterError, e:
			print "Invalid chapter", e.chapter
			print "Options are", \
				", ".join( s for s in dir( chapters )
						if s[0] != '_' and s != "NEVER" )
			return 1
	else:
		outDir = "tutorial"
		chapter = chapters.DEFAULT

	# If output directory not specified, make it the name of the chapter
	if not options.outdir:
		options.outdir = RES_PATH + "_" + outDir

	if isinstance( chapter, tuple ) or isinstance( chapter, list ):
		chapterList = chapter
		for chapter in chapterList:
			outputDir = RES_PATH + '_' + chapterToString( chapter ).lower()
			generateResForChapter( chapter, outputDir )
	else:
		generateResForChapter( chapter, options.outdir )

	return 0

def generateDefaultRes( outputDir ):
	generateResForChapter( chapters.DEFAULT, outputDir )

def generateResForChapter( chapter, outputDir ):
	print "Generating for chapter", chapter, '-', chapterToString( chapter )
	print "    from", RES_PATH
	print "    to", outputDir
	print

	tutorial.setChapter( chapter )

	# Macro to create an output filestream for the stripped copy of a file
	def outfile( fname, mode="w" ):
		fname = fname.replace( RES_PATH, outputDir )
		d, f = os.path.split( fname )
		if not os.path.isdir( d ):
			os.makedirs( d )
		return open( fname, mode )

	# Directory that we shouldn't go into because it is excluded
	currSkipDir = None
	skipDirs = set()

	for dir, subdirs, files in os.walk( RES_PATH ):
		if os.path.basename( dir ) in [ "CVS", ".svn" ]:
			currSkipDir = dir
			continue

		if currSkipDir and dir.startswith( currSkipDir ):
			# print "Skipping", dir
			continue

		currSkipDir = None

		if dir in skipDirs:
			currSkipDir = dir
			continue

		# Filter out files with known bad names
		for f in files[:]:
			for patt in EXCLUDE_PATTS:
				if re.search( patt, f ):
					files.remove( f )
					break

		# Read includes file in this directory if it exists
		try:

			for line in open( "%s/.include" % dir ):

				fname, chapter = line.split()
				path = os.path.join( dir, fname )
				chapter = stringToChapter( chapter )

				# If it's being included, skip to the next entry
				if tutorial.includes( chapter ):
					continue

				# Excluded directories go into the bad list
				if os.path.isdir( path ):
					skipDirs.add( path )

				else:
					# print "Skipping file", path
					files.remove( fname )

		except IOError, e:
			pass

		# Map all filenames to their full paths
		files = [os.path.join( dir, f ) for f in files]

		# Macro for grabbing all files of a particular type
		def fnames( *extns ):
			patt = re.compile( r"^.*\.(%s)$" % "|".join( extns ) )
			return filter( lambda f: patt.search( f ), files )

		# Strip xml files
		for f in fnames( "xml", "def" ):
			stripXML( f, outfile( f ) )
			filename = os.path.abspath( f )
			# print "Removing", filename, "from", files
			files.remove( filename )


		# Strip python scripts
		for f in fnames( "py" ):
			stripPy( f, outfile( f ) )
			files.remove( os.path.abspath( f ) )

		# Any remaining files should just be copied over
		for f in files:
			shutil.copyfileobj( open( f, "rb" ), outfile( f, "wb" ) )
			# print "Duping", f

if __name__ == "__main__":
	sys.exit( main() )

# generate_res_trees.py
