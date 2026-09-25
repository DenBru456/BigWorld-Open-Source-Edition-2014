import logging
import time
import os
import re
import sys
import telnetlib
from StringIO import StringIO

log = logging.getLogger( __name__ )


def runscript( procs, script = None, lockCells = False, outputs = None,
			   prefix = True ):

	if not procs:
		return False

	# If we are talking to cellapps, lock cells
	if lockCells:
		log.info( "Locking cells ..." )
		procs[0].user().getProc( "cellappmgr" ).shouldOffload( False )
		time.sleep( 0.5 )

	# Make sure script is terminated with a newline
	if script and not script.endswith( "\n" ):
		script += "\n"

	try:

		# If we are interactively connecting to a single app, use the real telnet
		# program so that non line-based input (i.e. 'up arrow') works
		if len( procs ) == 1 and not script:
			p = procs[0]
			watcherPort = p.getWatcherValue( "pythonServerPort" )
			if watcherPort == None:
				log.error( "Unable to retrieve python port from watcher tree. This "
					"can indicate incompatible watcher protocols (ie: 1.9 tools "
					"talking to 1.8 servers)." )
				# inverting return value as the os.system does below
				return 0

			# Everything seems ok, so lets continue
			port = int( watcherPort )
			return not os.system( "telnet %s %s" % (p.machine.ip, port) )

		conns = {}
		for p in procs:
			watcherPort = p.getWatcherValue( "pythonServerPort" )
			if watcherPort == None:
				log.error( "Unable to retrieve python port from watcher tree. This "
					"can indicate incompatible watcher protocols (ie: 1.9 tools "
					"talking to 1.8 servers)." )
				# inverting return value as the os.system does above
				return 0

			# Everything seems ok, so lets continue
			port = int( watcherPort )
			conns[ telnetlib.Telnet( p.machine.ip, port ) ] = p

		if script: script = StringIO( script )

		if outputs:
			assert len(procs) == len(outputs), \
				"Must have one file-like object per process"
			outputDict = dict( zip( procs, outputs ) )
		else:
			outputDict = None

		# Add prefix to output if we're using command line input
		addPrefix = outputDict == None and len( procs ) > 1

		# Macro to read server output
		def slurp( conn, line = "", silent = False, output = sys.stdout ):

			index, match, s = conn.expect( ["\n>>> ", "\n\.\.\. "] )
			more = (index == 1)

			if silent:
				return more

			s = s.replace( line, "", 1 )
			s = s[:-4]

			if not s:
				return more

			if addPrefix and prefix:
				s = "%-12s%s" % (conns[ conn ].label() + ":", s)

			output.write( s )
			output.flush()
			return more

		# Flush initial prompts
		for conn in conns:
			slurp( conn, silent = len( procs ) > 1 or script != None )

		more = False
		connOrder = sorted( conns.items(), key = lambda (c,p): p )

		# Macro for sending code and reading the response
		def sendAndRecv( line ):

			if outputDict:
				output = outputDict[ p ]
			else:
				output = sys.stdout

			more = False

			for conn, p in connOrder:
				conn.write( line )
				more = slurp( conn, line, output = output ) or more

			return more

		# Interact
		while True:
			if script:
				line = script.readline()
			else:
				try:
					# logical expression, used like a ternary operator
					line = raw_input( (more and "... ") or ">>> " ) + '\r\n'
				except EOFError:
					line = ""
				except KeyboardInterrupt:
					line = ""

			line = re.sub( "\r?\n$", "\r\n", line )
			line = re.sub( "\t", "    ", line )

			# Line is empty only when a the ScriptIO object has reached
			# the end of the string, or when Ctrl-D is pressed.
			if line:
				more = sendAndRecv( line )
			else:
				break


		# Flush final part of output if the script left the interpreter wanting
		# a final newline (i.e. prompt is stuck on "... ")
		if more:
			sendAndRecv( "\r\n" )

	# If we are talking to cellapps, unlock cells
	finally:

		if lockCells:
			procs[0].user().getProc( "cellappmgr" ).shouldOffload( True )
			if script == sys.stdin:
				log.info( "" )
			log.info( "Unlocked cells" )

	return True

# run_script.py
