#!/usr/bin/env python
"""   Start a server from a saved server layout.

   A new server will be started exactly as specified in the saved layout file
   <filename>. If any hosts specified in the layout are offline the server
   startup will fail."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return """load <filename>"""


def getHelpStr():
	return __doc__


def run( args, env ):
	filename = None
	if len( args ) > 0:
		filename = args[0]

	if filename == None:
		return env.usageError( "You must supply a filename!", getUsageStr )

	return env.getUser( fetchVersion = True ).startFromXML( filename )


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# load.py
