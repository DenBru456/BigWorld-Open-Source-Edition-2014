#!/usr/bin/env python
"""
This module provides an interface to bots functionality.  It allows addition,
removal, setting of bot parameters, and querying.
"""

import sys
import optparse

from pycommon import cluster
from pycommon import uid as uidmodule
from pycommon import util as pyutil

USAGE = """%prog: [options] <command> [args]; where <command> is one of:

  ls
    Displays information about currently running bots processes, as well as
    min/max/avg load for cellapps, baseapps, and bots processes.

  add [n]
    Add n bots to the server, or 1 if no number supplied.

  del [n]
    Delete n bots from the server, or 1 if no number supplied.

  movement <controller> <params>
    Set the movement controller for all bots.  You will usually want to use the
    'Patrol' controller, whose parameter format is 'graph-file[,options]', where
    options are:
    snap:        Bots will snap to a point on the graph (they just start moving
	             towards a point on the path by default).
    random:      Bots will move towards a random point on the graph (they will
                 move towards the nearest point on the graph by default).
    scalePos=n   Scale the graph by the given factor.
    scaleSpeed=n Scale the speed of the bots by the given factor.

  set [watcher value] [watcher value] ...
    Set watcher values on all bots processes.

  run [script]
    Run supplied script on all bots processes.  If no script is given, the
    script will be read from standard input.

  startprocs [n]
    Start n new bot processes on all candidate machines, or 1 if no number
    given."""

# ------------------------------------------------------------------------------
# Section: Main
# ------------------------------------------------------------------------------

# When run as a script
if __name__ == "__main__":
	pyutil.setUpBasicCleanLogging()

	opt = optparse.OptionParser( USAGE )
	opt.add_option( "-u", dest = "uid", default = uidmodule.getuid(),
					help = "Specify the UID or username to work with" )
	(options, args) = opt.parse_args()

	# Must specify uid manually on windows
	if options.uid == None:
		print "You must specify a UID"
		opt.print_help()
		sys.exit( 1 )

	c = cluster.Cluster()
	me = c.getUser( uidmodule.getuid( options.uid ) )
	writeLog = True

	if not me.serverIsRunning():
		print "server isn't running ... bailing out"
		sys.exit(1)

	if not args or args[0] == "ls":
		writeLog = False
		me.lsBots()

	elif args[0] == "add":
		numtoop = 1
		if len( args ) > 1:
			numtoop = int( args[1] )
		me.addBots( numtoop )

	elif args[0] == "del":
		numtoop = 1
		if len( sys.argv ) > 2:
			numtoop = int( args[1] )
		me.delBots( numtoop )

	elif args[0] == "movement":
		if len( args ) not in (3, 4):
			print "Usage: %s movement controllerType controllerData" % sys.argv[0]
			sys.exit()

		controllerType = args[1]
		controllerData = args[2]

		try:
			botTag = args[3]
		except:
			botTag = ""

		me.setBotMovement( controllerType, controllerData, botTag )

	elif args[0] == "set":

		setargs = args[1:]
		if len( setargs ) % 2 != 0:
			print "odd number of args passed to 'set' - aborting!"
			sys.exit(1)

		me.setWatchersOnAllBots( *zip( setargs[0::2], setargs[1::2] ) )

	elif args[0] == "run":

		try:
			me.runScriptOnBots( args[1] )
		except:
			me.runScriptOnBots()

	elif args[0] == "startprocs":

		if len( args ) > 1:
			n = int( args[1] )
		else:
			n = 1

		for bm in me.getBotMachines():
			for i in xrange( n ):
				bm.startProc( "bots", me.uid )

	else:
		print "Unknown command '%s'" % args[0]
		opt.print_help()

# bot_op.py
