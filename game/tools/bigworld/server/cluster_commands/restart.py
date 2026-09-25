#!/usr/bin/env python
"""   Restarts the server using the current server layout.
        """

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return "restart"


def getHelpStr():
	return __doc__



def run( args, env ):
	if args:
		env.warning( "Extra arguments given - %s", ', '.join( args ) )

	return env.getUser( fetchVersion = True ).restart()


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# restart.py
