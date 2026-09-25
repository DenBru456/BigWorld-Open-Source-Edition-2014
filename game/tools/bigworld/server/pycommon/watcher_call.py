import logging

from pycommon import cluster
from pycommon import watcher_data_type as WDT
from pycommon import watcher
from pycommon import watcher_constants as Constants
from pycommon import watcher_data_message
from watcher_call_base import WatcherCallBase, WatcherCallException
from watcher_data_message import WatcherDataMessage

log = logging.getLogger( __name__ )


# -----------------------------------------------------------------------------
# Watcher call class
# -----------------------------------------------------------------------------
class WatcherCall( WatcherCallBase ):
	"""
	Class which represents a function call exposed through watchers on
	a cellapp/baseapp/serviceapp/loginapp/bots/dbapp.
	Contains functionality for retrieving information about Watcher
	functions as well as executing them.
	"""

	validProcTypes = ["baseapp", "cellapp", "serviceapp", 
					"loginapp", "bots", "dbapp"]


	def __init__( self, user, watcherPath, procType, appId=None ):
		"""
		@param user         User to determine the apps to run the watchers.
		@param watcherPath  The watcher path that needs to be called.
	                        e.g. "command/addGuards"
		@param procType     A string which contains the process type that this
		                    function should be run on.
							Valid values are: "baseapp","cellapp", "serviceapp",
							"loginapp", "bots" and "dbapp".
		@param appId        A string which contains an ordinal number for the
							app to run on, e.g. "01".
		"""

		WatcherCallBase.__init__( self,
			procType = procType,
		)

		self.user 	= user
		self.appId 	= appId

		if isinstance( watcherPath, unicode ):
			self.watcherPath = watcherPath.encode( "utf8" )
		else:
			self.watcherPath = watcherPath

		self.argTypes = None


	def execute( self, args, output, timeout = 5 ):
		"""
		Runs a watcher call by calling the appropriate method either
		directly, or through the "forwardTo" watcher on cellappmgr or
		baseappmgr. The mgr will then forward the watcher call to the
		appropriate group of baseapp or cellapps.

		@param args     The list of arguments to send to the function.
		"""

		watcherTuple = self.convertArgs( args )

		wdm = WatcherDataMessage()
		wdm.message = wdm.WATCHER_MSG_SET2
		wdm.count   = 0

		target = self._getTargetProc()

		watcherDestPath = self._getExecutePath( target.version )
		log.debug( "Executing watcher path: %s", watcherDestPath )
		wdm.addSetRequest( watcherDestPath, watcherTuple )

		results = None

		try:
			# TODO: Replace the call to "sendWatcherMessages" with
			# messages.batchSet() or whatever it's going to be
			# called. This function should be the equivalent of 
			# batchQuery, except for Watcher SET messages instead.

			# Furthermore, we should probably remove the necessity
			# to build a WDM object and just be able to pass Python values
			# directly to this "batchSet" function.

			# e.g. messages.batchSet( target, args )

			results = self.sendWatcherMessages( [target], wdm, timeout )
		except WatcherCallException, e:
			output and output.addErrorMessage(
					"Error: %s: %s" % (type(e).__name__, e) )

		if output is not None and results is not None:
			self.outputResult( target, results, output )


	def outputResult( self, target, results, output ):
		result = results[target]

		if result[0] == False:
			output.addErrorMessage(
					"Function call did not execute successfully." )

		if result[1] is None:
			return

		output.addOutput( result[1][0].value )

		# Add the result from single component
		if self.appId or self.runType == Constants.EXPOSE_LOCAL_ONLY:
			output.addResult( "%s" % result[1][1].value )

		# Add the result from components
		else:
			for i in result[1][1]:
				name = None
				id = i.value[0].value
				value = i.value[1].value

				# Use type from result if exists
				if len( i.value ) == 3:
					type = int( i.value[2].value )
					if type == Constants.CELL_APP:
						name = "CellApp"
					elif type == Constants.BASE_APP:
						name = "BaseApp"
					elif type == Constants.SERVICE_APP:
						name = "ServiceApp"

				# Fallback to resolving name from target, this method cannot
				# distinguish BaseApp from ServiceApp
				elif target.component == "BaseAppMgrInterface":
					name = "BaseApp"
				elif target.component == "CellAppMgrInterface":
					name = "CellApp"

				output.addResult( "%s %s: %s\n" % (name, id, value) )


	def _getTargetProc( self ):
		"""
		Get process to run on. This may either be a direct target or
		a manager process.
		"""
		if self.appId is not None:
			return self.getTargetProcs( self.user, appId=self.appId )[0]
		else:
			return self.getTargetProcs( self.user )[0]



	def _getExecutePath( self, version ):
		"""
		Create the Watcher path that we need to call on the baseappmgr or
		cellappmgr.

		The mgr processes have a ForwardingWatcher located at "forwardTo".
		If appId is not set, set the path to use forwarding,
		otherwise leave it as is.
		e.g. The watcher path we use in order to run "command/addGuards" on
		     each baseapp would be: "forwardTo/all/command/addGuards". This
		     would be called on the baseappmgr.
		"""

		if self.appId is not None or self.runType == Constants.EXPOSE_LOCAL_ONLY:
			return self.watcherPath

		pathPrefix = watcher.Forwarding.runTypeHintToWatcherPath(
				self.runType, version  )

		return "/".join( [ pathPrefix, self.watcherPath ] ).strip( "/" )


	@classmethod
	def isValidProcType( cls, procType ):
		return procType.lower().replace(" ","") in cls.validProcTypes


	@classmethod
	def isValidRunType( cls, runType ):
		return runType is None or Constants.isValidExposure( runType )

# WatcherCall


def watcherFunctions( category, user ):
	"""
	Retrieve a list of watcher functions from a 
	baseapp/cellapp/loginapp/bots/dbapp
	(the first process of each type found is the one queried).

	If a category is specified, then we retrieve Watcher functions in the
	directory corresponding to that category. If category is a blank string,
	then get the list of Watcher functions directly under the top level
	"command" directory.

	@param category	The category for which we want the list of watcher
	functions.
					Corresponds to a directory under the top level "command"
					directory on the baseapp/cellapp/loginapp/bots/dbapp.
	@param user		User object for who we want the functions.
	"""

	# Scan baseapp/serviceapp, cellapp, loginapp, bots, dbapp
	procTypes = [t for t in WatcherCall.validProcTypes if t is not "serviceapp"]
	procs = [user.getProc( t ) for t in procTypes ]

	procs = [p for p in procs if p is not None]
	if not procs:
		return []

	watchers = []

	path = "command"
	if category:
		path += "/" + category

	result = WatcherDataMessage.batchQuery( [path], procs, 2 )
	for proc in procs:
		for t in result[proc].get( path, [] ):
			if t[3] == WatcherDataMessage.WATCHER_MODE_CALLABLE:
				call = WatcherCall( user, "%s/%s" % ( path, t[0] ), proc.name )
				watchers.append( call )

	return watchers


# watcher_call


