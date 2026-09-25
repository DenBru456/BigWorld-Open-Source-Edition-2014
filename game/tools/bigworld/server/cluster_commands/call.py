#!/usr/bin/env python
"""   Call a watcher function on an app."""

import re
from pycommon.watcher_call import WatcherCall, watcherFunctions
from pycommon.watcher_call_base import WatcherException

class ConsoleOutput( object ):
	""" A class which formats output resulting from running a watcher on the
	server, for the console """

	def __init__( self ):
		self.results = ""
		self.output = ""


	def addResult( self, result ):
		self.results = self.results + "\t" + result


	def addOutput( self, output ):
		self.output = "\n\t".join( output.splitlines() )


	def addErrorMessage( self, message, *args ):
		if args:
			message = message % args
		print message


	def printToConsole( self ):
		print "\n[Return Value]\n"
		print self.results
		print "[Console Output]\n"
		print self.output + "\n"

# ConsoleOutput

def getUsageStr():
	return "call [<watcher-path> <parameters>]"


def getHelpStr():
	return __doc__


def _splitProcessString( processString ):
	found = re.search( '\d', processString )
	if found:
		pos = found.start()
		return processString[:pos], processString[pos:]

	return processString, None


def listWatcherCalls( env ):
	user = env.getUser()
	functionCalls = watcherFunctions( None, user )
	env.info( "\n[Callable Watchers]\n" )
	for call in functionCalls:
		path = call.watcherPath.replace( "command/", "", 1 )
		#env.info( "\t%s (%s)" % (path, call.procType) )
		env.info( "\t%s" % path )
	print
		
def findProcType( user, path ):
	functionCalls = watcherFunctions( None, user )
	for call in functionCalls:
		if call.watcherPath == path:
			return call.procType

	return None

def run( args, env ):

	user = env.getUser()

	if len( args ) < 1:
		return listWatcherCalls( env )

	try:
		watcherPath = args.pop(0)
		watcherValue = args
	except IndexError:
		return env.usageError( "Insufficient arguments", getUsageStr )

	watcherPath = "command/" + watcherPath
	procType = findProcType( user, watcherPath )
	if procType is None:
		print "Could not find watcher '%s'" % watcherPath
		return False

	try:
		watcherCall = WatcherCall( user, watcherPath, procType )
		output = ConsoleOutput()
		watcherCall.execute( watcherValue, output )
		output.printToConsole()
	except WatcherException, e:
		print "Error: %s: %s" % (type(e).__name__, e)
		return False

	return True


# call.py
