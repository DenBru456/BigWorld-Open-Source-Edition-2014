#!/usr/bin/env python
"""   Kill the specified processes.

   Similar in behaviour to the 'kill' server command, by default this will send
   a SIGINT signal to the specified server processes causing the main loop to
   finish its current processing and then shutdown the process.

   Command Options:
    -c,--core:   Send a SIGQUIT insteand of SIGINT signal to the specified
                 server processes causing the process to terminate in its 
                 current state and generate a core dump for process state 
                 analysis."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util
from pycommon import messages

def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-c", "--core", action = "store_true",
					default = False )

	return sopt


def getUsageStr():
	return "killproc [-c|--core] <processes>"


def getHelpStr():
	return __doc__


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )
	
	shouldDumpCore = options.core
	processFilters = parsedArgs

	if not processFilters:
		return env.usageError( "No processes specified", getUsageStr )

	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		env.error( "No processes selected" )
		return False

	for process in processes:
		if shouldDumpCore:
			process.kill( messages.SignalMessage.SIGQUIT )
		else:
			process.kill()

	return True


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# killproc.py
