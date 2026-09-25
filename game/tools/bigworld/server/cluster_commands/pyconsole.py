#!/usr/bin/env python
"""   Connect the 'Python Console' of a BaseApp or CellApp server process.

   Telnets to the python server port on the given type of server process with
   the specified process ID.

   Example:
    To connect to whichever BaseApp owned an entity with ID 215

    control_cluster.py  pyconsole  --entity base:215

   Command Options:
    -e,--entity cell|base:<id>   Connect to server process owning Entity <id>
    -l,--lock-cells              Prevent cells offloading entities during
                                 script execution"""


if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util
from pycommon import process as process_module

import logging
log = logging.getLogger( __name__ )


def _buildOptionsParser():
	import optparse

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-e", "--entity" )
	sopt.add_option( "-l", "--lock-cells", action = "store_true",
					default = False )

	return sopt


def getUsageStr():
	return "pyconsole [<process> | -e|--entity <cell|base>:<id>] [-l|--lock-cells]"


def getHelpStr():
	return __doc__

class UsageError( Exception ):
	def __init__( self, msg ):
		self.msg = msg


def findProcessWithEntity( entityDescription, user ):
	import re

	match = re.search( "(cell|base):(\d+)", entityDescription )
	if match == None:
		raise UsageError( "You must pass (cell|base):<ID> to --entity, "
				   "e.g. --entity cell:2407" )

	appType = match.group( 1 ) + "app"
	entityID = int( match.group( 2 ) )

	# Find the entity
	log.info( "Scanning %ss for entity %d ...", appType, entityID )
	process = command_util.findProcessWithEntity( user, appType, entityID )

	if process == None:
		log.error( "Entity %d not found on any running %s",
					entityID, appType )
	else:
		log.info( "Entity %d found on %s", entityID, process.label() )

	return (process, entityID)


def run( args, env ):
	status = True

	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	shouldLockCells = options.lock_cells
	entityDescription = options.entity

	scriptToRun = None

	# Connect to entity
	if entityDescription != None:
		try:
			process, entityID = \
					findProcessWithEntity( entityDescription, env.getUser() )
		except UsageError, e:
			return env.usageError( e.msg, getUsageStr )

		if process:
			processes = [process]
			scriptToRun = "e = BigWorld.entities[ %d ]" % entityID
		else:
			status = False


	# Connect to process
	else:
		if not parsedArgs:
			return env.usageError( "No processes specified", getUsageStr )

		processes = env.getSelectedProcesses( parsedArgs )
		if not processes:
			env.error( "No processes selected" )
			return False

		elif len( processes ) > 1:

			if not isinstance( processes[ 0 ], process_module.BotProcess ):
				return env.usageError( "'pyconsole' only supports connecting "
						"to a single process", getUsageStr )

			env.warning( "Multiple bots processes running, "
				"using first returned" )
			processes = [ processes[ 0 ], ]

	if status:
		from pycommon import run_script
		if scriptToRun:
			status = run_script.runscript( processes, scriptToRun )

		status &= run_script.runscript( processes, lockCells = shouldLockCells )

	return status


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# pyconsole.py
