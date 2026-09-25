#!/usr/bin/env python
"""   Check that a currently running server matches the specified layout.

   The server layout provided by <filename> is expected to be a an XML server
   layout as generated with the 'save' command.  The layout is expected to
   exactly match the currently running processes."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "checklayout <filename>"


def getHelpStr():
	return __doc__


def run( args, env ):

	filename = None
	if len( args ) > 0:
		filename = args[0]

	if not filename:
		return env.usageError( "Expected a filename argument", getUsageStr )

	status = env.getUser().verifyLayoutIsRunning( filename )

	if status:
		env.info( "Server running according to layout" )
	else:
		env.info( "Server not running according to layout" )

	return status

if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# checklayout.py
