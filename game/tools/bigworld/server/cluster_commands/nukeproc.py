#!/usr/bin/env python
"""   Force the specified processes to shutdown causing a core dump.

   This command is deprecated and will be removed in a future version.

   See also: 'killproc'"""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "nukeproc <processes>"


def getHelpStr():
	return __doc__


def run( args, env ):
	env.warning( 'This command is deprecated and will be removed in a future' + 
					' version.' )

	from pycommon import messages

	processFilters = args
	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		return env.usageError( "No processes specified", getUsageStr )

	for process in processes:
		process.machine.killProc( process, messages.SignalMessage.SIGQUIT )

	return True


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# nukeproc.py
