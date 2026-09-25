"""
Contains the WatcherCall base class.
"""

# Import standard modules

# Import pycommon modules
from pycommon import watcher_data_type as WDT
from pycommon.watcher_data_message import WatcherDataMessage
from pycommon import watcher_constants as Constants

# -----------------------------------------------------------------------------
# WatcherCall base class
# -----------------------------------------------------------------------------
class WatcherCallBase( object ):
	"""
	Abstract WatcherCall object which represents a call to a watcher function 
	on the server.
	The most important method is the "execute" method, which runs the call.
	This class contains mechanism code to define how things work.
	Policy logic should be implemented in descendants of this class.
	"""
	watcherCallInfo = {}

	def __init__( self, procType=None,
			runType=None ):
		"""
		Base WatcherCall object.
		"""

		if not self.isValidProcType( procType ):
			raise WatcherException( "Invalid procType given: ", procType )

		if not self.isValidRunType( runType ):
			raise WatcherException( "Invalid runType given: ", runType )

		self.procType	= procType
		self.runType	= runType
		self.args	= None


	def execute( self, args, runType=None ):
		raise NotImplementedError( "Abstract method execute not implemented" )


	def getTargetProcs( self, user, useForwarder=True, appId=None ):
		"""
		Get the process which we'll call the watcher on.
		If useForwarder is set, then will run on the base/cellappmgr.
		Otherwise, check if specific appId requested.
		Else, grab the first app.
		"""

		# do not use forwarding if appId is set or runType is LOCAL_ONLY
		if appId is not None or self.runType == Constants.EXPOSE_LOCAL_ONLY:
			useForwarder = False

		if useForwarder:
			if self.procType == "cellapp":
				proc = user.getProc( "cellappmgr" )
				if proc: return [proc]
				else: raise WatcherCallException( "No cellappmgr available" )

			elif self.procType == "baseapp" or self.procType == "serviceapp":
				proc = user.getProc( "baseappmgr" )
				if proc: return [proc]
				else: raise WatcherCallException( "No baseappmgr available" )

			else:
				raise WatcherCallException( 
					"Cannot use forwarder for procType %r!" % self.procType )
		else:
			# If useForwarder is False, then we're most likely getting
			# an actual component so we can query it for "__doc__" and
			# "__args__"
			if appId is None:
				proc = user.getProc( self.procType )
			else:
				proc = user.getProcExact( self.procType + appId )

			if proc: 
				return [proc]
			else: 
				if appId is None:
					raise WatcherCallException( "No " + self.procType + " available" )
				else:
					raise WatcherCallException( "No " + self.procType + appId + " available" )

		raise Exception( "wha? %s" % (self.procType) )


	def sendWatcherMessages( self, procs, wdm, timeout = 5 ):
		"""
		Given a WatcherDataMessage and a list of processes,
		send the WDM to each process.

		TODO: This function should be replaced by cluster.batchSet() or
		whatever it's to be called.
		"""

		replies = WatcherDataMessage.tcpMainLoop( wdm, procs, timeout )
		if not replies:
			raise WatcherCallException( "No replies (maybe it timed out?)" )

		reply = replies[procs[0]].values()[0]
		return { procs[0] : (reply[0][4], reply[0][1]) }


	def convertArgs( self, args ):
		"""
		Will convert the args to WDT objects to be sent to the watcher.
		"""

		if not self.args:
			self.retrieveInfo()

		outArgs = []
		argCount = 0
		try:
			for name, type in self.args:
				argValue = args[argCount]
				if not isinstance( argValue, type.value):
					#print "Converting %r to %r" % (argValue, type.value)
					wdt =  type.value( argValue )
				else:
					wdt = argValue
				outArgs.append( wdt )
				argCount = argCount + 1
		except ValueError, e:
			raise WatcherCallException( 
				"Cannot convert argument %r to required type %r" % \
				(argValue, type.value) )
		except IndexError, e:
			raise WatcherCallException( 
				"Insufficient function call arguments: expected %r, got %r" % \
				(len(self.args), argCount) )

		return  WDT.WatcherDataTypeTuple( outArgs )


	def retrieveInfo( self ):
		"""
		Retrieve information from the server about how to call the 
		watcher.
		This will fill in the following attributes:
		  - args 	 :  Argument list of (name, WatcherDataType type object) pairs
		  - desc 	 :  Description of call
		  - runType	 : Expose type.
		"""
		watcherArgPath = self.watcherPath + "/__args__"
		watcherDocPath = self.watcherPath + "/__doc__"
		watcherExposePath = self.watcherPath + "/__expose__"

		t = self.getTargetProcs( self.user, useForwarder=False,
			appId=self.appId )[0]
		r = WatcherDataMessage.batchQuery(
				[watcherArgPath, watcherDocPath, watcherExposePath], [t], 1 )

		self.args	= r[t][watcherArgPath][0][1]
		self.desc 	= r[t][watcherDocPath][0][1]

		# allows custom runType to remain
		if self.runType is None:
			self.runType = r[t][watcherExposePath][0][1]

		if self.runType is None:
			raise WatcherCallException( "Function '%s' cannot be found." % \
				self.watcherPath )

# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class WatcherException(Exception):
	pass


class WatcherCallException(WatcherException):
	pass

# watcher_call_base
