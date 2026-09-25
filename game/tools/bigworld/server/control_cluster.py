#!/usr/bin/env python
"""Command line utility for running operations on a cluster."""

import sys
import optparse
import socket
import logging

from pycommon import machine # TODO: For VERBOSE, a little dodgy
from pycommon import command_util
from pycommon import user
from pycommon import util as pyutil

log = logging.getLogger( 'control_cluster' )


USAGE = """%(script)s [options] [command] [command-options] [command-args]

 Control Cluster provides a functionality for interacting with and controlling
BigWorld server processes.

Options:
   -u|--user  <user>    Username or UID to perform commands as.
   -m|--machine         Hostname or IP of machine to perform commands on
   -v|--verbose         Enable verbose command and debugging output.
   -h|--help            Display help for a command.

Available Commands:

   Help for a command is available by providing the help command with an
   argument such as '%(script)s help command'

    Server Commands:               Process Commands:
      start                          startproc
      stop                           killproc
      kill                           restartproc
      nuke                           retireproc
      restart

      check                          getmany
      checkcores                     get
      display                        set
      summary                        call
      nagios                         pyconsole
                                     runscript
      checklayout
      load
      save

    Cluster Commands:              Profiling Commands:
      cinfo                          profile
      log                            eventprofile
      mdlist                         mercuryprofile
      netinfo
      querytags
      users

      checkring
      pingring
      flush

Miscellaneous help:
  For more information on machine and process selection, please refer to the
  following help pages.

   --help process-selection
   --help machine-selection"""


PROCESS_SELECTION_HELP_STRING = \
""" Control Cluster Process Selection
 =================================

  Commands that involve process selection support any of the following methods:

  * Exact process name, e.g. 'cellapp01', 'cellappmgr', 'bots:bwdev13:1287'
  * All processes of a type, e.g. 'cellapps', 'baseapps', 'bots'
  * Single process of a type, e.g. 'cellapp'
  * Non-zero-padded numbering, e.g. 'cellapp1'
  * Machine:PID (needed only for bots processes), e.g. 'bwdev13:1287'
  * All processes (useful for looking at watchers): 'all'
  * Multiple processes at once (space seperated): 'baseapp01 cellapp03'

  When selecting a single process of a type, if there is more than one running,
  the process will be chosen randomly from the available set.

  The advantage of the non-zero-padded numbering method is that it allows
  shell expansions such as 'cellapp{1..5}' or 'baseapp{1,5,7}'. Please see
  the shell expansion section of your shells manual page for more details.
"""


MACHINE_SELECTION_HELP_STRING = \
""" Control Cluster Machine Selection
 =================================

  Commands that involve machine selection support any of the following methods:

  * Exact machine name, e.g. 'bw01'
  * Exact IP address, e.g. '10.40.7.1'
  * Wildcard match on hostname, e.g. 'bw*'
  * BWMachined version, e.g. 'version:42'
  * BWMachined group, e.g. 'group:blue'
  * All machines can be explicitly selected with 'all'

  Additionally, the pattern ':noprocs:' matches any machine that has no
  processes registered with bwmachined, and is useful for finding machines
  on the network that are available for use.

  The fastest machine that is not currently running any processes can be
  selected with ':best:'.

  For most commands, if the <machines> argument to a command is optional (as
  indicated in help by square brackets [<machines>], not specifying any
  machines will select *all* machines in the server cluster.

  BWMachined groups are listed in the [Groups] tag in /etc/bwmachined.conf."""

HELP_STRINGS = {
"process-selection" : PROCESS_SELECTION_HELP_STRING,
"machine-selection" : MACHINE_SELECTION_HELP_STRING }


def run():
	status = True
	logging.getLogger().setLevel( logging.INFO )

	# Now inject all the commands into the option list
	opt = optparse.OptionParser( add_help_option = False )
	opt.add_option( "-u", "--user", dest = "uid", default = None,
					help = "Specify the UID or username to work with" )
	opt.add_option( "-m", "--machine", dest = "machine", default = None,
					help = "Specify the machine work with" )
	opt.add_option( "-v", "--verbose", dest = "verbose", action = "store_true",
			help = "Enable verbose debugging output" )
	opt.add_option( "-h", "--help", dest = "help", action = "store_true",
		   			help = "Display help for a command" )

	# This option allows us to have custom options after our commands,
	# eg: control_cluster.py start --bots
	opt.allow_interspersed_args = False
	options, args = opt.parse_args()

	# Enable verbosity if desired
	if options.verbose:
		machine.VERBOSE = True
		logging.getLogger().setLevel( logging.DEBUG )

	if args and args[0] == "help":
		options.help = True
		args = args[ 1: ]

	# Need to handle --help slightly differently due to optparse wanting
	# to process anything that looks like an option.
	if options.help:
		return displayHelp( *args[:1] )

	# Set up logging system
	logFormatter = pyutil.CleanFormatter()
	logHandler = logging.StreamHandler( sys.stdout )
	logHandler.setFormatter( logFormatter )
	logging.getLogger().addHandler( logHandler )	
	
	command = "display"
	if len( args ) > 0:
		command = args[0]

	env = command_util.CommandEnvironment( options.uid, options.verbose,
			options.machine )

	try:
		return runCommand( command, args[1:], env )

	except user.UserError, ue:
		print str( ue )
		return False

	except socket.error, se:
		print se[ 1 ]
		return False


def getCommandModule( command, isVerbose = False ):
	try:
		module = __import__( "cluster_commands." + command,
					globals(), locals(), [""] )
	except ImportError, e:
		if isVerbose:
			print "Failed to import module for command %s:" % command, e
		return None

	return module


def runCommand( command, args, env ):
	module = getCommandModule( command, env.isVerbose )

	try:
		f = getattr( module, "run" )
	except AttributeError:
		# Note: module may be None or not have a run function
		log.error( "Unknown command '%s'\n" % command )
		displayHelp()
		return False

	return f( args, env )


def displayTopLevelHelp():
	print USAGE % {"script": sys.argv[0] }
	return True


def displayHelp( command = None ):
	if command is None:
		return displayTopLevelHelp()

	if HELP_STRINGS.has_key( command ):
		print HELP_STRINGS[ command ]
		return True

	module = getCommandModule( command )

	if not module:
		print "No help available for unknown command '%s'" % command
		return False

	try:
		usageFunc = getattr( module, "getUsageStr" )
		helpFunc = getattr( module, "getHelpStr" )
	except AttributeError:
		print "No help available for command '%s'" % command
		return False

	print usageFunc()
	print
	print helpFunc()

	return True


if __name__ == "__main__":
	try:
		sys.exit( not run() )
	except KeyboardInterrupt:
		sys.exit( 1 )

# control_cluster.py
