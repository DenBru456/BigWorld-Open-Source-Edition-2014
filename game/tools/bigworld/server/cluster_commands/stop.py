#!/usr/bin/env python
"""   Shut down the server in the most controlled way possible.

   This is the preferred method of shutting down a server which will ensure
   players are logged off and entity data is saved to the database in a
   graceful manner. This command should always be used unless the server is
   in a bad state which required requires more drastic shutdown.

   See also: 'kill' and 'nuke'"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "stop"


def getHelpStr():
	return __doc__


def run( args, env ):
	if args:
		env.warning( "Extra arguments given - %s", ', '.join( args ) )

	return env.getUser( fetchVersion = True ).smartStop()


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# stop.py
