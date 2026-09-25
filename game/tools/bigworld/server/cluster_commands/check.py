#!/usr/bin/env python
"""   Indicate whether a server is running.

   A simple message is output indicating whether there is an active server
   running as well as returning with an exit status of 0 if there is an
   active server. If no server is active a non 0 exit value will be returned."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util

def getUsageStr():
	return "check"


def getHelpStr():
	return __doc__


def run( args, env ):
	if args:
		env.warning( "No arguments expected" )

	status = True

	user = env.getUser()

	if command_util.isServerRunning( user ):
		env.info( "Server running for %s" % user )
	else:
		env.info( "Server not running for %s" % user )
		status = False

	return status


if __name__ == "__main__":
	import sys

	from pycommon import util as pyutil
	pyutil.setUpBasicCleanLogging()

	sys.exit( command_util.runCommand( run ) )

# check.py
