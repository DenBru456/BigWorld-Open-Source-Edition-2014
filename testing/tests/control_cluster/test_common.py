import re

from bwtest import config
from helpers.command import Command
from helpers.timer import runTimer, TimerError

path = "%s/%s/tools/bigworld/server/control_cluster.py" % \
		( config.CLUSTER_BW_ROOT, config.BIGWORLD_FOLDER )

def run_cc_command( command, params, ccParams = [], parallel = False, 
				ignoreErrors = False, input = None ):
	cmd = Command()
	prefix = ""
	if ignoreErrors:
		prefix = "- "
	ret = cmd.call( "%spython %s %s %s %s" % \
				(prefix, path, " ".join( ccParams ), command, " ".join( params )),
				parallel = parallel, waitForCompletion = not parallel,
				input = input )
	output = None
	if cmd._lastOutput:
		output = cmd._lastOutput[0] 
	return ret, output

def noUnexpectedOutput( output ):
	expectedWarning = "WARNING:  Still waiting for"
	isExpected = True
	for line in output.split( "\n" ):
		line = line.strip()
		if line and expectedWarning not in line:
			isExpected = False
	return isExpected

def checkForProc( cc, procType, procOrd, timeout, exists ):
	def check():
		return ( cc.findProc( procType, procOrd ) != None ) == exists
	try:
		runTimer( check, timeout = timeout )
	except TimerError:
		return False
	return True


def checkForPatterns( patterns, output ):
	for pattern, count in patterns:
		values = re.findall( pattern, output )
		if len( values ) != count:
			print "Missing pattern: %s" % pattern
			return False
	return True


def checkIfSorted( output, column, columnOrder, pattern, reverse = True ):
	entries = re.findall( pattern, output )
	columnId = columnOrder.index( column )
	try:
		subFields = [ float( e.strip().split()[columnId] ) for e in entries ]
	except:
		subFields = [ e.strip().split()[columnId] for e in entries ]
	return sorted( subFields, reverse = reverse) == subFields