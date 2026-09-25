#!/usr/bin/env python

# Checks source files (cpp, hpp, rc, etc) to see if they contain localisation
# tokens, and if so, matches them against the language files in order to find
# out if there are any missing localisation strings.
#
# Usage: python chk_lang.py [-en|-cn|-<2-letter lang code>] [src_dir [lang_dir]]
#        The -en flag checks english languange files, and -cn checks chinese, or
#        the a two letter language code that matches the desired language files.
#        If src_dir is not specified, then the default src path is used.
#        If lang_dir is not specified, then the default languange path is used.
#

from os.path import join, getsize
import os
import sys
import shutil
import time
import distutils.util
import xml.parsers.expat


g_lang = "_en"
g_stringDatabase = []
g_xmlTagStack = []
g_xmlString = ""


#-------------------------------------------------------------------------------
# xml-parsing functions
#-------------------------------------------------------------------------------

def xmlStartElement(name, attrs):
	global g_xmlTagStack
	global g_xmlString
	g_xmlString = ""
	g_xmlTagStack.append( name )


def xmlEndElement(name):
	global g_xmlTagStack
	global g_xmlString
	global g_stringDatabase

	# if the string in the tag is good, add the tag path to the string database
	if g_xmlString:
		thisString = ""
		count = 0
		for elem in g_xmlTagStack:
			# skip the first two tags, they are "root" and "en"
			if count >= 2:
				# build tag path
				if len( thisString ) > 0:
					thisString = thisString + "/"
				thisString = thisString + elem
			else:
				count = count + 1
				
		g_xmlString = ""
		g_stringDatabase.append( thisString )

	g_xmlTagStack.pop()


def xmlCharData(data):
	global g_xmlString
	c = repr(data)
	# build a string with actual letters, numbers and other printable characters
	# to later skip tags that only contain characters such as spacees, \n,etc.
	if c != "\n" and c != "\r" and c != "\t" and c != " ":
		g_xmlString = g_xmlString + c


# This function get's rid of non-ascii chars in the XML file before parsing, so
# the XML parsing doesn't fail. Our Chinese language files have these kind of
# characters.
def cleanLine( line ):
	retLine = ""
	for c in line:
		code = ord( c )
		if code < 32 or code > 127:
			retLine = retLine + " "
		else:
			retLine = retLine + c
			
	return retLine
	
	
def parseLanguageFile( fname ):
	global g_stringDatabase
	
	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = xmlStartElement
	p.EndElementHandler = xmlEndElement
	p.CharacterDataHandler = xmlCharData

	fileData = ""
	f = open( fname )
	try:
		for line in f:
			line = cleanLine( line )
			fileData = fileData + line
	finally:
		f.close()
	
	p.Parse( fileData, 1 )


def buildStringDatabase( path ):
	global g_lang
	
	os.chdir( path )
	found = False
	for root, dirs, files in os.walk( "." ):
		# remove the preceding "./" to create cleaner paths
		if root[0:2] == ".\\" or root[0:2] == "./":
			root = root[2:]
		elif root == ".":
			root = ""

		for name in files:
			if name[-7:] == g_lang + ".xml":
				fname = join( root, name )
				print "- Adding language file " + fname + " ..."
				fname = join( path, fname )
				parseLanguageFile( fname )
				found = True
	if not found:
		print "ERROR: Cannot find language files for language " + g_lang + "."
		sys.exit(-1)


#-------------------------------------------------------------------------------
# file functions
#-------------------------------------------------------------------------------

# check here files you want to exclude from the final package
def isSourceFile( name ):
	if name[-4:] == ".cpp" or name[-4:] == ".hpp" or name[-4:] == ".ipp" or name[-2:] == ".c" or name[-2:] == ".h":
		return True
	return False


def isResourceFile( name ):
	if name[-3:] == ".rc":
		return True
	return False


# add here directories you want to exclude from the final package
def stripUnwantedDirs( root, dirs ):
	# don't visit CVS directories
	try:
		dirs.remove('CVS')
	except:
		pass

	# don't visit SVN directories
	try:
		dirs.remove('.svn')
	except:
		pass

	# don't visit unwanted directories
	try:
		dirs.remove('third_party')
		dirs.remove('python')
		dirs.remove('resmgr')
	except:
		pass


#-------------------------------------------------------------------------------
# core functions
#-------------------------------------------------------------------------------

#
def isLocalisationToken( token ):
	if len( token ) < 3:
		return False
		
	if token != token.upper():
		return False
		
	alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	foundLetter = False
	foundSlash = False
	for c in token:
		if c == " " or c == "\\":
			return False
			
		if c == "/":
			foundSlash = True
			
		if not foundLetter and alphabet.find( c ) != -1:
			foundLetter = True
			
	return foundSlash and foundLetter

	
#
def checkToken( token, fname ):
	if token[0] == "`":
		token = token[1:]
	
	try:
		index = g_stringDatabase.index( token )
	except ValueError:
		print "" + token + "\t\t\t\t" + fname


# check that the file's strings are in the language files
def checkSourceFile( name ):
	global g_stringDatabase

	f = open( name )
	try:
		for line in f:
			# for each line, search for one or more localised tokens
			start = 0
			while start < len( line ) and start != -1:
				start = line.find( "\"", start )
				end = -1
				if start != -1:
					end = line.find( "\"", start + 1 )
					if end != -1:
						token = line[ start + 1 : end ]
						if isLocalisationToken( token ):
							# found a localised token, look for it in the database
							checkToken( token, name )
								
					if end == -1:
						start = start + 1
					else:
						start = end + 1
						
	finally:
		f.close()


# check that the file's strings are in the language files
def checkResourceFile( name ):
	global g_stringDatabase
	
	f = open( name )
	try:
		for line in f:
			# for each line, search for one or more localised tokens
			start = 0
			while start < len( line ) and start != -1:
				start = line.find( "\"`", start )
				end = -1
				if start != -1:
					end = line.find( "\"", start + 1 )
					if end != -1:
						# found a localised token, look for it in the database
						checkToken( line[ start + 2 : end ], name )
								
					if end == -1:
						start = start + 1
					else:
						start = end + 1
						
	finally:
		f.close()


def check( srcPath, langPath ):
	print ""
	print "Building localisation string database from XML files..."
	buildStringDatabase( langPath )
	
	print ""
	print "Checking localisation strings (missing string and file)"
	os.chdir( srcPath )
	for root, dirs, files in os.walk( "." ):
		# remove the preceding "./" to create cleaner paths
		if root[0:2] == ".\\" or root[0:2] == "./":
			root = root[2:]
		elif root == ".":
			root = ""

		for name in files:
			srcFile = isSourceFile( name )
			resrcFile = isResourceFile( name )
			if srcFile or resrcFile:
				fname = join( root, name )
				#print "- Checking " + fname + " ..."
				fname = os.path.abspath( fname )
				if srcFile:
					checkSourceFile( fname )
				elif resrcFile:
					checkResourceFile( fname )

		stripUnwantedDirs( root, dirs )
	print ""
	print ""


#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

def doMain():
	global g_lang
	
	i = 1
	
	if len( sys.argv ) > i and sys.argv[i][0] == "-":
		print "Checking language " + sys.argv[i][1:] + "."
		g_lang = "_" + sys.argv[i][1:]
		i = i + 1
	else:
		print "No language specified, checking English language files."

	srcPath = '../../../src'
	if len( sys.argv ) > i:
		try:
			srcPath = sys.argv[i]
			i = i + 1
			if not os.path.exists( srcPath ):
				print "ERROR: Cannot find source path " + srcPath
				sys.exit(-1)
		except IndexError:
			pass

	langPath = '../../../res/helpers/languages'
	if len( sys.argv ) > i:
		try:
			langPath = sys.argv[i]
			i = i + 1
			if not os.path.exists( langPath ):
				print "ERROR: Cannot find language files path " + langPath
				sys.exit(-1)
		except IndexError:
			pass

	check( srcPath, langPath )


if __name__ == "__main__":
	doMain()
# bin_convert.py
