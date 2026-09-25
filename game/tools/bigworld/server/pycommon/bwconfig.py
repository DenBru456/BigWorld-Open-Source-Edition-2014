"""
This provides similar functionality to bwconfig.hpp.
Typical usage would be:

import bwconfig

bwconfig.get( "baseApp/secondaryDB/enable", False )
"""

import os
import pwd
from xml.etree.ElementTree import ElementTree, Element


configChain = None


def get( xpath, default = None ):
	"""
	This method returns a configuration value. The default
	is returned if not found.
	"""

	global configChain

	if not configChain:
		parseChain()

	xpath = cleanXPath( xpath )

	for config in configChain:
		root = config[1].getroot()
		elements = root.findall( xpath )

		if elements:
			return elements[0].text.strip()

	return default


def set( xpath, value ):
	"""
	This method sets a configuration. Non-existing elements on
	the xpath are created.
	"""

	global configChain

	if not configChain:
		parseChain()

	xpath = cleanXPath( xpath )

	# First in the chain is authoritive
	configFile = configChain[0]
	root = configFile[1].getroot()

	# Get leaf element
	elements = root.findall( xpath )
	if elements:
		element = elements[0]
	else:
		# Walk xpath, creating non existing elements
		element = root
		parts = xpath.split( "/" )
		partialXPath = ""

		for part in parts:
			if partialXPath:
				partialXPath += "/"
			partialXPath += part

			elements = root.findall( partialXPath )

			if elements:
				element = elements[0]
			else:
				newElement = Element( part )
				element.append( newElement )
				element = newElement

	element.text = value

	# Write to file
	configFile[1].write( configFile[0] )


def cleanXPath( xpath ):
	"""
	This method cleans up a xpath.
	"""

	# No leading '/'
	if xpath[0] == "/":
		xpath = xpath[1:]

	# No trialing '/'
	if xpath[-1] == "/":
		xpath = xpath[:-1]

	return xpath


def resPaths( user = None ):
	"""
	This method returns the paths on the resource tree.
	"""

	paths = []

	homedir = os.environ['HOME'];
	if user:
		homedir = pwd.getpwnam( user ).pw_dir


	f = file( homedir + "/.bwmachined.conf", "r" )
	lines = f.readlines()
	f.close()

	for l in lines:
		l = l.strip()
		if (len( l ) > 0) and (not l.startswith( '#' )):
			l = l.replace( "\n", "" )
			try:
				paths = l.split( ";" )[1].split(':')
			except Exception, e:
				raise Exception( 'Malformed line in .bwmachined.conf: ' + l )
			break

	return paths


def find( resource, paths = None, user = None ):
	"""
	This method returns the full path of a file in a resource
	tree. None is returned if not found.
	"""

	if paths == None:
		paths = resPaths( user )

	for p in paths:
		p = p + os.sep + resource
		if os.access( p, os.F_OK ):
			return p

	return None


def parseChain( username = "" ):
	"""
	This method parses the configuration file chain and returns
	a list of (filename, xml.etree.ElementTree) tuples ordered by
	chain position.
	"""

	filename = None
	if username:
		filename = find( "server/bw_%s.xml" % username, 
				user = username )
	else:
		filename = find( "server/bw.xml" )

	global configChain
	configChain = []

	while filename:
		tree = ElementTree()
		root = tree.parse( filename )
		configChain.append( (filename, tree) )

		# Check for parent
		parentFiles = root.findall( "parentFile" )

		if parentFiles:
			filename = parentFiles[0].text.strip()
			filename = find( filename, user = username )
		else:
			filename = None


def resetChain( username = "" ):
	global configChain
	parseChain( username )
