#!/usr/bin/env python
"""   Non-interactively run a Python script on server processes.

   Note: This option should generally only be used in a development environment
         and be used with EXTREME caution in a production environment due to
         the potential for a bad script to shut down or crash an active server.

   If no script file is provided, script input will be read from stdin.

   Command Options:
    -P,--no-prefix    Disable prefixing script input lines with ">>> ". This 
                      option only works when running a script on multiple 
                      processes
    -l,--lock-cells   Prevent cells offloading entities during script execution
"""

import os

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util
from pycommon import process as process_module

def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-P", "--no-prefix", action = "store_true" )
	sopt.add_option( "-l", "--lock-cells", action = "store_true",
					default = False )

	return sopt


def getUsageStr():
	return "runscript <processes> [<filename>] [-l|--lock-cells] [-P|--no-prefix]"


def getHelpStr():
	return __doc__


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	shouldLockCells = options.lock_cells
	shouldPrefix = not options.no_prefix

	# The python script file can only be the last argument
	# If the last argument is neither a filename with '.py' extension nor a valid 
	# process name, it will be treated as python script file
	lastArgument = parsedArgs[-1]
	scriptContents = None
	if lastArgument.endswith( ".py" ):
		scriptContents = open( lastArgument ).read()
		parsedArgs.pop()
	else:
		for procName in process_module.Process.types.serverProcs(): 
			if lastArgument.startswith( procName ):
				#The last argument is like a process name, so don't treat it as
				#python script file	
				break
		else:
			#The last argument is neither a filename with '.py' extension 
			#nor a valid process name, treat it as python script file
			if os.path.isfile( lastArgument ):
				scriptContents = open( lastArgument ).read()
				parsedArgs.pop()

	processFilters = parsedArgs
	if not processFilters:
		return env.usageError( "No processes specified", getUsageStr )

	processes = env.getSelectedProcesses( processFilters )

	if not processes:
		env.error( "No processes selected" )
		return False
	
	for proc in processes:
		if not proc.hasPythonConsole:
			env.error( "Seleted process '%s' doesn't support Python Console" % proc.name )
			return False

	from pycommon import run_script
	return run_script.runscript( processes, scriptContents,
							   lockCells = shouldLockCells,
							   prefix = shouldPrefix )


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# runscript.py
