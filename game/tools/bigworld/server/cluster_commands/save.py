#!/usr/bin/env python
"""   Save the current server layout.

   Saves an XML file to <filename> specifying the currently active BigWorld
   server processes along with the hostnames they are active on."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


from pycommon import command_util


def getUsageStr():
	return "save <filename>"


def getHelpStr():
	return __doc__


def run( args, env ):
	filename = None
	if len( args ) > 0:
		filename = args[0]

	if filename == None:
		return env.usageError( "You must supply a filename!", getUsageStr )

	return env.getUser().saveToXML( filename )


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# save.py
