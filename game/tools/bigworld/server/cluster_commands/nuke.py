#!/usr/bin/env python
"""   Do a forced shutdown of the server using SIGQUIT.

   This command is deprecated and will be removed in a future version.

   This method of server shutdown is a last resort mechanism to kill a server
   that has otherwise become unresponsive. It forces processes to terminate
   in their current state and will cause a process core dump for each active
   process in order to assist diagnosing any issues with the server.

   Note: If you have previously shutdown a server with the 'stop' or 'kill'
         commands and it is still not completely shutdown, this may be due
         to the processes releasing memory or other resources they had in
         use. Shutdown time can vary greatly depending on the load of the
         server.

   See also: 'stop' and 'kill'"""


if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "nuke"


def getHelpStr():
	return __doc__


def run( args, env ):
	env.warning( 'This command is deprecated and will be removed in a future' + 
				' version.' )

	if args:
		env.warning( "Extra arguments given - %s", ', '.join( args ) )

	from pycommon import messages
	return env.getUser().stop( messages.SignalMessage.SIGQUIT )

if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil	

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# nuke.py
