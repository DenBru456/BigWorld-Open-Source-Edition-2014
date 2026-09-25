"""
This provides simple injection functionality for
~/.bwmachined.conf
"""

import os

from bwtest import config, log
from command import MultiUserWriter


def getNonTestConfig():
	"""This function returns the active non-test bin and res paths
	as a tuple (bin, res)
	"""
	lines = _readLines()

	return _getNonTestConfig( lines )


def setTestConfig( testBinPath, testResPaths, user ):
	"""This function sets the test config
	if either of testBinPath or testResPaths is an empty string,
	it defaults to the active non-test config
	@param testBinPath: Path to BigWorld binaries
	@param testResPaths: List of path to game res-trees
	@param user: User that we are setting the config for
	"""
	formPaths = None
	if type( testResPaths ) == str:
		formPaths = testResPaths
	else:	
		formPaths = ":".join( testResPaths )

	_setTestConfig( testBinPath, formPaths, False, user )


def clearTestConfig( user ):
	"""This function clears the test config
	@param user: User that we are clearing the config for
	"""
	return _setTestConfig( "", "", True, user )


# Section: helpers
def _setTestConfig( testBinPath, testResPaths, doClear, user ):
	binPath = testBinPath
	resPaths = testResPaths

	lines = _readLines( user )

	if not testBinPath and not doClear:
		binP, res = _getNonTestConfig( lines )
		binPath = binP

	if not testResPaths and not doClear:
		binP, res = _getNonTestConfig( lines )
		resPaths = res

	newLines = []
	
	for line in lines:
		res = _testLine( line )
		if res == "test":
			break

		resLine = line

		if res == "active":
			if doClear:
				pass
			else:
				resLine = "#@#" + line

		if res == "inactive":
			if doClear:
				resLine = line[3:]
			else:
				pass

		if resLine and resLine != "\n":
			newLines.append( resLine )

	if not doClear:
		newLines.append( "\n" )
		newLines.append( "## Temporary configuration for testing\n" )
		newLines.append( binPath + ";" + resPaths + "\n" )
	_writeLines( newLines, user )

	return True


def _getConfigPath( user ):
	return '/home/' + user + "/.bwmachined.conf" 


def _readLines( user ):
	try:
		fo = open( _getConfigPath( user ), "r" )
		lines = fo.readlines()
		fo.close()
		return lines
	except:
		return [""]


def _writeLines( lines, user ):
	try:
		fo = MultiUserWriter( _getConfigPath( user ) )
		fo.writelines( lines)
		fo.close()
	except:
		log.error( "Cannot write config to %s" % _getConfigPath( user ) )
		pass


def _getNonTestConfig( lines ):
	foundLine = None
	for line in lines:
		res = _testLine( line )
		if res == "active":
			foundLine = line
			break
		if res == "inactive":
			foundLine = line[3:]
			break
		if res == "test":
			break

	if foundLine is None:
		return ( "", "" )

	split = foundLine.split(";")
	binP = split[0]
	res = split[1]

	return (binP, res)


def _testLine ( line ):
	line = line.lstrip().rstrip( " \t\n:" )
	if "## Temporary" in line:
		return "test";
	if line.find( "#@#" ) == 0:
		return "inactive"
	if line.find( "#" ) == 0:
		return "comment"
	if ";" in line:
		return "active"
	return "none"


