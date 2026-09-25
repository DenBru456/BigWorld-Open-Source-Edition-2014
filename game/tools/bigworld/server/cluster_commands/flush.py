#!/usr/bin/env python
"""   Force machines to flush their tags and user mappings."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )


def getUsageStr():
	return "flush [<machines>]"


def getHelpStr():
	return __doc__


def run( args, env ):
	status = True

	machines = env.getSelectedMachines( args )

	for machine in machines:
		env.info( machine.getFormattedStr() )

	if not machines:
		status = False
	else:
		for machine in machines:
			status = machine.flushMappings() and status

	return status


if __name__ == "__main__":
	import sys
	from pycommon import command_util
	from pycommon import util as pyutil

	pyutil.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# flush.py
