#!/usr/bin/env python
"""   Do a forced shutdown of the server.

   This method of server shutdown will forcefully tell the server processes to
   terminate regardless of what they are currently doing.
   
   The default method of terminating using this command is by sending a SIGINT
   signal. While no data loss should occur using SIGINT, a connected client's
   user experience will be suddenly stopped and the database will have a sudden
   influx of incoming data.

   Command Options:
    -c,--core:   Send a SIGQUIT instead of SIGINT signal to the server
                 processes, causing them to terminate in their current state and
                 generate a core dump for each running process in order to assist
                 diagnosing an issues with the server. This method of server
                 shutdown is a last resort mechanism to kill a server that has
                 otherwise become unresponsive.

                 Note: If you have previously shutdown a server with the 'stop'
                 command or by using the 'kill' command with the default SIGINT
                 signal and it is still not completely shutdown, this may be due
                 to the processes releasing memory or other resources they had
                 in use. Shutdown time can vary greatly depending on the load of
                 the server.

   See also: 'stop'"""


if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import messages

def _buildOptionsParser():
	import optparse

	usageStr = "usage: " + getUsageStr()
	sopt = optparse.OptionParser( add_help_option = False, usage = usageStr )
	sopt.add_option( "-c", "--core", action = "store_true",
					default = False )

	return sopt


def getUsageStr():
	return "kill [-c|--core]"


def getHelpStr():
	return __doc__


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	shouldDumpCore = options.core

	if parsedArgs:
		env.warning( "Extra arguments given - %s", ', '.join( parsedArgs ) )

	if shouldDumpCore:
		return env.getUser().stop( messages.SignalMessage.SIGQUIT )
	else:
		return env.getUser().stop()


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# kill.py
