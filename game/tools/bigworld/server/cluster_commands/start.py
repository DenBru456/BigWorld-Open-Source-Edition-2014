#!/usr/bin/env python
"""   Start the server on the specified set of machines.  To start the server on
   all machines, you must explicitly pass 'all' for machine selection.

   Command Options:
    -b,--bots:      Allocate machines for and start bots processes
    -r,--revivers:  Start revivers on each machine used
    -s,--simple:    Only start a single CellApp and BaseApp (default)
    -S,--several:   Start a server utilising as many CPU cores as are available.
                    This option will result in multiple BaseApp and CellApp
                    processes starting at once.
    -t,--tags:      Restrict what processes can be started on each machine by
                    its [Components] tag list as specified in
                    /etc/bwmachined.conf.
    --bwConfig:     Choose to start machine on debug or hybrid mode."""

if __name__ == "__main__":
	import bwsetup
	bwsetup.addPath( ".." )

from pycommon import command_util


def getUsageStr():
	return """start <machines>"""


def getHelpStr():
	return __doc__


def _buildOptionsParser():
	import optparse
	from pycommon.cluster_constants import BW_SUPPORTED_CONFIGS, \
			BW_CONFIG_HYBRID

	sopt = optparse.OptionParser( add_help_option = False )
	sopt.add_option( "-b", "--bots", action = "store_true" )
	sopt.add_option( "-r", "--revivers", action = "store_true" )
	sopt.add_option( "-s", "--simple", action = "store_true" )
	sopt.add_option( "-S", "--several", action = "store_true", default = False )
	sopt.add_option( "-t", "--tags", action = "store_true", default = True )
	sopt.add_option( "--bwConfig", type = "choice", action = "store",
			choices = BW_SUPPORTED_CONFIGS, default = BW_CONFIG_HYBRID )

	return sopt


def run( args, env ):
	sopt = _buildOptionsParser()
	(options, parsedArgs) = sopt.parse_args( args )

	useSimpleLayout = not options.several

	if options.simple:
		env.warning( "Option '--simple' has been deprecated and has no effect. "
			"This option is now enabled by default" )

	return command_util.genericServerStart( env,
				machines = parsedArgs,
				startBots = options.bots,
				startRevivers = options.revivers,
				obeyBWmachinedTags = options.tags,
				useSimpleLayout = useSimpleLayout,
				getUsageStr = getUsageStr,
				bwConfig = options.bwConfig )


if __name__ == "__main__":
	import sys
	import pycommon.util

	pycommon.util.setUpBasicCleanLogging()
	sys.exit( command_util.runCommand( run ) )

# start.py
