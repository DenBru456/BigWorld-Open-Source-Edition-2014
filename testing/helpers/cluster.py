"""This module contains all the classes and methods used for controlling
the BigWorld cluster
"""
import os
import pickle
from datetime import datetime
import time
import sets

import pycommon.command_util

from pycommon import cluster
from pycommon import util, messages, command_util
from pycommon import bwconfig
from pycommon import watcher_constants as Constants

from pycommon.watcher_call import WatcherCall, watcherFunctions
from pycommon.watcher_call_base import WatcherException

import timer
import command
import bwmachined_conf
from bwtest import config
from bwtest import log
from bwtest import TestCase
from primitives import mysql, locallog
from error import HelperError




class WatcherOutput( object ):
	""" A class which formats output resulting from running a watcher on the
	server, for the console """

	def __init__( self ):
		"""Constructor.
		"""
		self.status = "waiting"
		self.result = None
		self.output = None
		self.exception = ""


	def isOk( self ):
		"""Status check method.
		@return boolean. True if status==ok
		"""
		return self.status == "ok"


	def printOutput( self ):
		"""Unimplemented method. Comment in print statement for
		additional debug information.
		"""
		pass
		# print "[bwtest][info] WatcherOutput:\n ", self.output


	def getException( self ):
		"""@return Exception string
		"""
		return self.exception

	def addResult( self, result ):
		"""Callback method used by pycommon to return result.
		@param result: Result string sent from pycommon
		"""
		# print "[bwtest][info] WatcherOutput.addResult: ", result
		#TODO: Handle one baseapp being ok and the other one failed
		if result.startswith( "error:" ):
			self.exception = ": " + result[6:]
			self.status = "error"
			return

		self.status = "ok"
		self.result = result
		if "ok:" in result:
			try:
				self.result = pickle.loads( result[3:] )
			except:
				pass


	def addOutput( self, output ):
		"""Callback method used by pycommon to return output
		@param output: Output string sent by pycommon
		"""
		# print "[bwtest][info] WatcherOutput.addOutput: ", output
		self.output = output
		pass


	def addErrorMessage( self, message, *args ):
		"""Callback method used by pycommon to return error messages. Just sets
		status to error
		@param message: Error message string sent by pycommon.
		"""
		# print "[bwtest][info] WatcherOutput.addErrorMessage: ", message
		self.status = "error"


class ClusterControllerError( HelperError ):
	"""Error class for error states in the cluster.
	eg. The cluster processes not starting
	"""
	pass


class CoreDumpError( ClusterControllerError ):
	"""Error class for when core dumps were found after stopping the server.
	"""
	
	def __init__( self, appList ):
		"""Constructor.
		@param appList: List of server processes that had core dumps.
		"""
		self.failedAppList = appList
		ClusterControllerError.__init__( self,
			"Found core dumps after the cluster "
			"has stopped: %r" % appList )


class ClusterController( object ):
	""" 
	This class helps control the cluster in auto-test environment
	"""

	def __init__( self, resPaths, load = False, user = config.CLUSTER_USERNAME,
				db = config.CLUSTER_DB_DATABASENAME ):
		"""Constructor.
		@param resPaths: Path to res-tree to be used. Can be relative to
		testing root or absolute. Can take a single path or a list of paths
		@param load: Set this to True if you want test to use loadmachines
		from user_config.xml
		@param user: Username to use. Overrides user_config.xml
		@param db: DB to use. Overrides bw_username.xml
		"""
		self._hasStarted = False
		self._timeout = 30
		self.user = user
		self.db = db
		self._machines = config.CLUSTER_MACHINES
		if ( load and config.CLUSTER_MACHINES_LOAD ):
			self._machines = config.CLUSTER_MACHINES_LOAD

		self._enableCoreDumpChecking = True

		self._setupPaths( resPaths )

		self.bots = Bots( self )

		self.clearDB()
		
		self.tempSnippetCount = 0

		# TODO: Make optional
		self.messageLogger = locallog.MessageLogger( self.user )
		self.messageLogger.start()

		if (config.BW_CONFIG == "debug"):
			self.setConfig( "allowInteractiveDebugging", "true")


	def clean( self ):
		"""Cleanup method that should be called in tearDown of test cases.
		Deletes temporary configuration files and stops messagelogger"""

		try:
			command.remove( self._tempTree )
		except command.CommandError:
			import traceback
			traceback.print_exc()

		bwmachined_conf.clearTestConfig( self.user )

		self.messageLogger.stop()


	# -------------------------------------------------------------------------
	# Public methods

	def start( self, layoutXML = None ):
		"""
		This method starts the cluster.
		
		@param layoutXML:	Use this parameter to start the server with a 
							non-standard layout
		"""

		user = self.getUser()
		procs = user.getServerProcs()

		if procs:
			procList = ', '.join( [p.name for p in procs] )
			log.error( "ClusterController.start(): attempt to start cluster "
					"when there are processes running: %s", procList )
			self.stop()
	
		user.cluster = cluster.cache.get( uid = user.uid )
		
		if layoutXML:
			log.info( "Starting Server for user %s for specified layout" % \
						user.name )
			succeeded = user.startFromXML( layoutXML, bwConfig=config.BW_CONFIG )
		else:
			log.info( "Starting Server for user %s on machines %s" % \
						( user.name, self._machines ) )
			selectedMachines = command_util.selectMachines( user.cluster,
														self._machines )
			if selectedMachines:
				selectedMachinesMap = {}
				for m in selectedMachines:
					selectedMachinesMap[ m.name ] = m
				selectedMachines = \
						[ selectedMachinesMap[n] for n in self._machines ]
				log.info( "Selected Machines: %s" % \
						[ m.name for m in selectedMachines ] )
				succeeded = user.start( selectedMachines, useSimpleLayout = True, 
										bwConfig=config.BW_CONFIG )
			else:
				succeeded = False

		if not succeeded:
			self.getUser().smartStop( forceKill=True )
			coreDumpList = self._checkForCoreDumps()

			if coreDumpList:
				raise CoreDumpError( coreDumpList )
			else:
				raise ClusterControllerError( "Failed to start the cluster" )


	def stop( self , timeout = 20 ):
		"""This method stops the cluster
		@param timeout: Use this to change how long to wait until all
		processes are stopped.  Default 20s"""

		user = self.getUser()
		res = user.smartStop( forceKill=True, timeout=timeout )


		if not res:
			raise ClusterControllerError( "Failed to stop the cluster" )

		def callableMethod():
			procs = self.getUser().getServerProcs()
			if procs:
				return False
			return True

		try:
			timer.runTimer( callableMethod, timeout = timeout )
		except timer.TimerError:
			procs = self.getUser().getServerProcs()
			procList = ', '.join( [p.name for p in procs] )
			log.info( "Failed to perform controlled shutdown in %d sec, " 
						"killing the cluster forcibly. "
						"The processes still running: %s", 
						timeout, procList )
			user = self.getUser()
			res = user.smartStop( forceKill=True )
			if not res:
				raise ClusterControllerError( "Failed to stop the cluster" )

		coreDumpList = self._checkForCoreDumps()
		if coreDumpList: 		
			raise CoreDumpError( coreDumpList )


	def startProc( self, procType, procCount = 1, machineIdx = 0 ):
		"""
		This method starts a process on a given machine
		
		@param procType: type of process, eg. 'baseapp'
		@param procCount: number of processes to run
		@param machineIdx: index of machine
		"""

		user = self.getUser()
		maxMachines = len( self._machines )
		
		if machineIdx < 0 or machineIdx >= maxMachines:
			raise ClusterControllerError( "Bad machine index (%d) "
				"max number of machines = %d" % (machineIdx, maxMachines) )

		machine = self._machines[ machineIdx ]
		log.info( "Starting %r process of type %s for user %s on machine %s" % \
			 ( procCount, procType, user.name, machine ) )
		selectedMachines = command_util.selectMachines( user.cluster,
							[machine] )
		res = user.startProc( selectedMachines[0], procType, 
							procCount, bwConfig=config.BW_CONFIG )
		if not res:
			raise ClusterControllerError( "Failed to start process %s on %s" %
										(procType, machine) )
		
		return res


	def retireProc( self, procType, procOrd = None ):
		"""
		This method initiates and waits for the retirement of a process.

		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""
		if type(procOrd)==int: 
			procOrd = "%02d" % procOrd
		proc = self.findProc( procType, procOrd )
		if proc is None:
			raise ClusterControllerError( "Failed to retire process %s" %
										self._procName( procType, procOrd ) )

		proc.retireApp()
		
		startTime = time.time()
		while self.findProc( procType, procOrd ): 
			if time.time() - startTime > self._timeout:
				raise ClusterControllerError( 
										"Timed out trying retire process %s" %
										self._procName( procType, procOrd ) )



	def killProc( self, procType, procOrd = None, forced = False ):
		"""
		This method kills and waits for the death of a process.

		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		@param forced: Set this to True to use SIGKILL when killing the process
		"""

		if type(procOrd)==int: procOrd = "%02d" % procOrd
		proc = self.findProc( procType, procOrd )
		if proc is None:
			raise ClusterControllerError( "Failed to kill process %s" %
										self._procName( procType, procOrd ) )

		signal = None
		if forced:
			signal = messages.SignalMessage.SIGKILL

		label = proc.label
		proc.machine.killProc( proc, signal = signal )
		
		startTime = time.time()
		while self.getUser().getProcExact( label ):
			if time.time() - startTime > self._timeout:
				raise ClusterControllerError( 
										"Timed out trying retire process %s" %
										label )


	def setTimeout( self, timeout ):
		""" 30 seconds by default, the timeout may be extended
		for special cases
		@param timeout: New timeout
		"""
		self._timeout = timeout


	def loadSnippetModule( self, procType, procOrd = None, path = "self_test" ):
		"""Makes a server app load a given module
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		@param path: path to module to load
		"""
		if type(procOrd)==int: procOrd = "%02d" % procOrd
		watcherCall = WatcherCall( self.getUser(),
								"command/callTestSnippet",
								procType,
								procOrd )
		
		if procType == "baseapp":
			watcherCall.runType = Constants.EXPOSE_BASE_APPS
		elif procType == "serviceapp":
			watcherCall.runType = Constants.EXPOSE_SERVICE_APPS

		fullPath = config.TEST_ROOT + "/res_trees/snippets/" + path
		output = WatcherOutput()
		args = pickle.dumps( { 'path': fullPath } )
		watcherCall.execute( [ "loadModule", args ], output )

		if not output.isOk() or not output.result:
			raise ClusterControllerError( "Failed to load snippet module "
					"'%s' on %s%s: %s" % ( path, procType, procOrd or '',
										output.getException() ) )

		return True


	def waitForApp( self, procType, procOrd = None ):
		"""
		This method waits for a given app to start
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""

		if type(procOrd)==int: procOrd = "%02d" % procOrd
		watcherCall = WatcherCall( self.getUser(),
								"command/callTestSnippet",
								procType,
								procOrd )

		def callableMethod():
			output = WatcherOutput()
			watcherCall.execute( [ "hasAppStarted", None ], output )

			if not output.isOk():
				raise ClusterControllerError( "waitForApp() failed "
						"on %s" % self._procName( procType, procOrd ) ) 

			# print "[bwtest][info] ClusterController.waitForApp() res = ", \
			#			output.result 
			return output.result

		try:
			timer.runTimer( callableMethod, lambda res: res )
		except timer.TimerError:
				raise ClusterControllerError( "waitForApp() timed out "
						"on %s" % self._procName( procType, procOrd ) ) 

	def waitForAppStop( self, procType, procOrd = None , timeout = 20):
		"""
		This method waits for a given app to stop
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		@param timeout: Specifies the wait period for the App to stop. Default 20s
		"""

		if type(procOrd)==int: procOrd = "%02d" % procOrd
		def callableMethod():
			proc = self.findProc( procType, procOrd )
			return proc is None
		try:
			return timer.runTimer( callableMethod, timeout = timeout )
		except timer.TimerError:
			return False


	def callOnApp( self, procType, procOrd = None, 
						snippetName = "hasAppStarted" , timeout = 5, **args ):
		""" 
		This method calls an existing snippet on a server app and 
		returns the result from a watcher.
		May raise an Exception if the call takes longer than
		timeout or fails on the server app. 
		Most of the results should be True, False or None
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		@param snippetName: String name of snippet to execute.
		@param timeout: Change how long to wait for snippet to execute. Default 5s
		""" 
		if type(procOrd)==int: procOrd = "%02d" % procOrd
		log.info( "callOnApp: calling via watcher on process %s",
			"%s%s" % (procType, procOrd or '') )

		watcherCall = WatcherCall( self.getUser(),
								"command/callTestSnippet",
								procType,
								procOrd )


		output = WatcherOutput()
		watcherCall.execute( 
						[ snippetName, pickle.dumps( args ) ], output, timeout )

		if not output.isOk():
			output.printOutput()
			raise ClusterControllerError( "Failed to call snippet '%s' "
					"on %s%s%s" % 
					( snippetName, procType, procOrd or '', 
					output.getException() ) )

		return self._waitForWatcher( procType,
									procOrd,
									"testing/lastResult" )


	def sendAndCallOnApp( self, procType, procOrd = None, 
						  snippet = "srvtest.finish()", timeout = 5, **args ):
		"""Load a tempory snippet from string and execute it on process.
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier Default None will provide
		the first process
		@param snippet: String containing Python code to execute.
		@param timeout: Change how long to wait for snippet to execute. Default 5s
		"""
		# create a temp file with this snippet
		self.tempSnippetCount += 1
		modName = "tempSnippet%s"  % self.tempSnippetCount
		snippetFilePath = config.TEST_ROOT + \
				"/res_trees/snippets/%s.py" % modName

		replDict = {}
		for k, v in args.items():
			val = str( v )
			if type( v ) is str:
				val = '"' + val + '"'
			replDict[ "{" + k + "}" ] = val

		def parse( line ):
			parsed = line
			for k, v in replDict.items():
				if line.find( k ) >= 0:
					parsed = parsed.replace( k, v )

			return parsed			

		lines = [ '\t' + parse( l ) + '\n' for l in snippet.split( '\n' ) ]

		lines.insert( 0, "import BigWorld, srvtest\n" )
		lines.insert( 1, "@srvtest.testSnippet\n" )
		lines.insert( 2, "def %s():\n" % modName)

		fo = command.MultiUserWriter( snippetFilePath )
		fo.writelines( lines )
		fo.close()

		def removeFile():
			
			try:
				command.remove( snippetFilePath )
				command.remove( snippetFilePath + "c" )
			except command.CommandError:
				pass

		try:
			time.sleep(0.1)
			self.loadSnippetModule( procType, procOrd, modName )
			res = self.callOnApp( procType, procOrd, modName, timeout )
			removeFile()
			return res
		except:
			removeFile()
			raise


	def callWatcher( self, procType, watcherName, procOrd = None, *args ):
		""" 
		This method calls an existing callable watcher on a server app and 
		returns the result from a watcher.
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		@param watcherName: Name of watcher to call. Provide any args to watcher
		after this parameter
		""" 
		if type(procOrd)==int: procOrd = "%02d" % procOrd
		watcherCall = WatcherCall( self.getUser(),
								"command/%s" % watcherName,
								procType,
								procOrd )


		output = WatcherOutput()
		watcherCall.execute( args, output )

		if not output.isOk():
			output.printOutput()
			raise ClusterControllerError( "Failed to call watcher '%s' "
					"on %s%s%s" % 
					( watcherName, procType, procOrd or '', output.getException() ) )

		return output.result


	def getUser( self ):
		"""Returns user object from pycommon
		"""
		env = command_util.CommandEnvironment( self.user )
		user = env.getUser( refreshEnv = True )
		user.cluster = cluster.cache.get( uid = user.uid ) 
		return user


	def clearDB( self ):
		"""
		This method recreates mysql and xml databases used by cluster.
		It's always called at ClusterController creation
		but you may need to call it explicitly
		"""
		if config.CLUSTER_DB_TYPE == "mysql":
			mysql.executeSQL( "DROP DATABASE IF EXISTS %s" % 
							self.db, useDB = False )
			mysql.executeSQL( "CREATE DATABASE %s" % 
							self.db, useDB = False )

		elif config.CLUSTER_DB_TYPE == "xml":
			path = self.getXmlDB()
			if path:	
				try:
					command.remove( path )
					log.info( "clearDB: Removed XML db file %s" % path )
				except command.CommandError:
					log.error( "clearDB: Fail to remove XML db file %s" % path )


	def syncDB( self ):
		"""
		This method calls the sync_db command to reinitialize
		mysql databases used by the cluster
		"""
		cmd = command.Command()
		cmd.call( "{bwroot}/%s/%s/commands/sync_db" 
				% (config.BIGWORLD_FOLDER, config.SERVER_BINARY_FOLDER ) )


	def getXmlDB( self ):
		"""
		This method returns the first location of a db.xml file
		found in the res path
		"""
		path = self.findInResPath( "scripts/db.xml" )
		if path is None:
			log.info( "getXmlDB: no Xml DB files found." )

		return path

	def getSecondaryDBCount( self ):
		"""Returns current amount of secondary databases
		"""
		count = mysql.executeSQL( "SELECT COUNT(*) "
							"FROM bigworldSecondaryDatabases" )[0][0]
		return count


	def getSecondaryDBPath( self ):
		"""Returns current configured path for secondary databases.
		"""
		secDBPath = self.getConfig("db/secondaryDB/directory", 
					config.TEST_ROOT + 
					"/res_trees/simple_space/res/server/db/secondary/")

		if not secDBPath.startswith( '/' ):
			secDBPath = config.TEST_ROOT + "/res_trees/simple_space/res/"\
			 + secDBPath 

		return secDBPath


	def getSecondaryDBFiles( self ):
		"""Returns a list of paths to current secondary databases
		"""
		secDBPath = self.getSecondaryDBPath()

		secFiles = [ os.path.join(secDBPath, f) for f in os.listdir( secDBPath ) 
					if f.find( self.user ) >= 0 and
						f.find( ".db" ) >= 0 ]

		return secFiles


	def cleanSecondaryDBs( self ):
		"""Remove all current secondary databases
		"""
		files = self.getSecondaryDBFiles()
		for fileName in files:
			command.remove( fileName )


	def getConfig( self, xpath, default = None ):
		""" 
		This method is just a wrapper on pycommon.bwconfig.get().
		It should be called after a ClusterController object is
		constructed so that the proper config chain is searched.
		@param xpath: config path, i.e. 'dbApp/type'
		@param default: default value to return in case the given path 
						is not found
		"""
		return bwconfig.get( xpath, default )


	def setConfig( self, xpath, value ):
		""" 
		This method is just a wrapper on pycommon.bwconfig.set().
		It should be called after a ClusterController object is
		constructed so that the proper config is modified.
		@param xpath: config path, i.e. 'dbApp/type'
		@param value: value to set
		"""
		log.info( "ClusterController: Setting config property '%s' to '%s'" 
			% ( xpath, value ) )
		return bwconfig.set( xpath, value )


	def setCoreDumpChecking( self, enable = True ):
		"""Sets whether we should check for core dumps when stopping the server.
		@param enable: Set True to enable core dump checking.
		"""
		self._enableCoreDumpChecking = enable

	
	def setWatcher( self, path, value, procType, procOrd = 1 ):
		"""Sets the value of specified watcher
		@param path: xpath expression of watcher
		@param value: Value to set watcher to
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""
		if type(procOrd)==int:
			procOrd = "%02d" % procOrd
		proc = self.findProc( procType, procOrd )
		if proc is None:
			raise ClusterControllerError( "Failed to find process %s%s "
							"for watching" % ( procType, procOrd ) )
		return proc.setWatcherValue( path, value )


	def getWatcherValue( self, path, procType, procOrd = 1):
		"""
		Returns the value of specified watcher
		
		@param path: xpath expression of watcher
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""

		return self.getWatcherData(path, procType, procOrd).value


	def getWatcherData( self, path, procType, procOrd = 1):
		"""
		Returns the data of specified watcher
		
		@param path: xpath expression of watcher
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""

		if type(procOrd)==int:
			procOrd = "%02d" % procOrd
		proc = self.findProc( procType, procOrd )
		
		if proc is None:
			raise ClusterControllerError( "Failed to find process %s%s "
							"for watching" % ( procType, procOrd ) )

		return proc.getWatcherData( path )


	def getWatcherByPid( self, pid, path ):
		"""
		Returns a watcher for a given path on a given PID.
		
		@param pid: PID of process to get watcher from
		@param path: xpath expression for watcher
		"""

		log.info( "Fetching watcher %r:%s for user %s" % \
					( pid, path, self.getUser().name ) )
		proc = None
		procs = self.getUser().getProcs()
		
		for p in procs:
			if p.pid == pid:
				proc = p
				break
			ret = None

		if proc:
			ret = proc.getWatcherData( path )

		log.info( "getWatcher returns %s" % ret )
		return ret


	def waitForWatcherValue( self, path, value, procType, procOrd = 1 ):
		"""
		Waits for watcher to be at a specific value
		
		@param path: xpath expression of watcher
		@param value: Value to wait for
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""
		
		if type(procOrd)==int:
			procOrd = "%02d" % procOrd
		
		proc = self.findProc( procType, procOrd )
		if proc is None:
			raise ClusterControllerError( "Failed to find process %s%02d "
							"for watching" % ( procType, procOrd ) )
		pid = proc.pid

		while ( True ):
			startTime = datetime.now()
			while ( True ):

				watcherData = proc.getWatcherData( path )
				if ( watcherData.value == value ):
					return True
				if ( ( datetime.now() - startTime ).seconds > self._timeout ):
					return False
				time.sleep( 1 )

	
	def waitForServerSettle( self, timeout = 20 ):
		"""
		Waits for events on server that happen after it is already 
		technically started.
		
		@param timeout: How long to wait before triggering error. Default 20s
		"""
		# for now, just check for presence of watchers in baseappmgr and cellappmgr
		# look for alpha dbapp to see if service apps are required, and if so, check
		# the service app to be operational as well.

		user = self.getUser()
		log.info( "waitForServerSettle for user %s" % user )
		startTime = datetime.now()
		cellappmgr = None
		dbapp = None

		while True:
			if dbapp and cellappmgr:
				break
			pids = self.getPids( "cellappmgr" )
			if pids:
				cellappmgr = pids[0]
			pids = self.getPids( "dbapp" )
			for pid in pids:
				if self.getWatcherByPid( pids[0], "isAlpha" ).value:
					dbapp = pids[0]
					break
			currTime = datetime.now()
			if (currTime - startTime).seconds > timeout:
				log.info( 
					"waitForServerSettle: timeout expired. No manager processes" )
				return False
			time.sleep( 1 )
		
	
		while( True ):
			checksPassed = 0
	
			if self.getWatcherByPid( cellappmgr, 'hasStarted' ).value:
				checksPassed = checksPassed + 1
	
			if self.getWatcherByPid( dbapp, 'hasStarted' ).value:
				checksPassed = checksPassed + 1
			
			if checksPassed > 1:
				break
		
			currTime = datetime.now()
			if (currTime - startTime).seconds > timeout:
				log.info( "waitForServerSettle: timeout expired" )
				return False
	
			time.sleep( 1 )
	
		# now that required apps are up, check for optional service app
		if self.getWatcherByPid( dbapp, 'config/desiredServiceApps' ).value > 0:
			log.info( "waitForServerSettle: checking serviceApp readiness" )
	
			while( True ):
				serviceapps = self.getPids( "serviceapp" )
				if serviceapps:
					break;
	
				currTime = datetime.now()
				if (currTime - startTime).seconds > timeout:
					log.info( "waitForServerSettle: timeout expired" )
					return False
	
				time.sleep( 1 )
	
	
			serviceapp = serviceapps[0]
			while( True ):
				checksPassed = 0
				if self.getWatcherByPid( serviceapp, 'isServiceApp' ).value:
					checksPassed = checksPassed + 1
	
				if checksPassed > 0:
					break
	
				currTime = datetime.now()
				if (currTime - startTime).seconds > timeout:
					log.info( "waitForServerSettle: timeout expired" )
					return False
	
				time.sleep( 1 )
	
		currTime = datetime.now()
		log.info( "waitForServerSettle: server OK. Time waited: %r" % (currTime - startTime).seconds )
		return True

	
	def waitForServerShutdown( self, timeout = 20 ):
		"""Wait for all processes to have shutdown.
		@param timeout: How long to wait before triggering error. Default 20s
		"""
		def callableMethod():
			procs = self.getUser().getServerProcs()
			if procs:
				return False
			return True

		try:
			return timer.runTimer( callableMethod, timeout = timeout )
		except timer.TimerError:
			return False


	def mangleResTreeFile( self, path, editorFunction ):
		"""
		Edit a file in the resource tree for purposes of this test.
		editorFunction needs to take two parameters, the file to read from and the
		file to write to.
		@param path: Path to file to be mangled
		@param editorFunction: Python function that will be called on the file.
		Should expect a file object to read and a file object to write
		"""
		inputPath = self.findInResPath( path )
		if inputPath is None:
			log.error( "mangleResTreeFile: No such file %s in resource tree" % ( path, ) )
			return False
		outputPath = self._tempTree + "/" + path
		outputDir, outputFile = os.path.split( outputPath )

		try:
			command.mkdir( outputDir )
		except command.CommandError, e:
			log.error( "mangleResTreeFile: Failed to create dir %s: %s" % ( outputDir, e ) )
			return False

		try:
			inputFile = open( inputPath, "r" )
		except IOError, e:
			log.error( "mangleResTreeFile: Failed to open %s for reading: %s" % ( inputPath, e ) )
			return False

		try:
			outputFile = command.MultiUserWriter( outputPath )
		except IOError, e:
			inputFile.close()
			log.error( "mangleResTreeFile: Failed to open %s for writing: %s" % ( outputPath, e ) )
			return False

		isOK = True
		try:
			editorFunction( inputFile, outputFile )
		except Exception, e:
			log.error( "mangleResTreeFile: Exception while processing %s: %s" % ( path, e ) )
			isOK = False
			
		inputFile.close()
		outputFile.close()

		if isOK:
			log.info( "mangleResTreeFile: Mangled %s to %s" % ( inputPath, outputPath ) )

		return isOK


	def lineEditResTreeFile( self, path, lineEditorFunction ):
		"""
		Edit a file in the resource tree for purposes of this test.
		Each line of the file is passed to lineEditor, and the
		return value replaces that line
		@param path: Path to file to be mangled
		@param lineEditorFunction: Python function that will be called on each line
		Should expect a string parameter which is the line to edit
		"""
		def lineEditorWrapper( inputFile, outputFile ):
			for line in inputFile:
				outputFile.write( lineEditorFunction( line ) )

		return self.mangleResTreeFile( path, lineEditorWrapper )


	# -------------------------------------------------------------------------
	# Private helpers

	def findInResPath( self, path ):
		"""
		Find a file in our res_trees
		@param path: Resource path to find
		"""
		for tree in self._resPaths:
			input = tree + "/" + path
			log.info( "findInResPath: looking for %s" % input )
			#HACK: This does the same as os.path.exists but gets
			# around problems with NFS file handle caching
			try:
				files = os.listdir( os.path.dirname( input ) )
				if os.path.basename( input ) in files:
					return input
			except:
				pass
		return None


	def findProc( self, procType, procOrd ):
		"""Returns the process object from pycommon.
		@param procType: type of process, eg. 'baseapp'
		@param procOrd: process ordinal, eg. 1,2,3... or other identifier
		"""
		if procOrd is None:
			return self.getUser().getProc( procType )
		return self.getUser().getProcExact(
			self._procName( procType, procOrd ) )
		
	
	def findProcsByMachine( self, procType, machineName ):
		"""Returns the list of processes matching procType
			on the specified machine
		@param procType: type of process, eg. 'baseapp'
		@param machineName: machine name, eg. 'qa02'
		"""
		procs = self.getUser().getProcs( procType )
		ret = []
		for proc in procs:
			if proc.machine.name == machineName:
				ret.append( proc )
		return ret


	def getProcs( self, filterByProcName = None, filterByProcPid = None ):
		""" Returns the list of procs running on the server for a user.
			If procName and/or procPid is supplied, filters out procs to
			return those matching given name and/or pid.
		@param filterByProcName: List of proc names to filter by
		@param filterByProcPid: List of PIDs to filter by
		"""

		procs = self.getUser().getProcs( filterByProcName )
		ret = []
		for proc in procs:
			if not filterByProcPid or proc.pid == filterByProcPid:
				ret.append( proc.name )

		log.info( "getProcs: returns %r" % ret )

		return ret
	
	
	def getPids( self, processname, machine = None ):
		""" Returns a list of pids for processes matching process name.
		@param processname: Type of process, eg. 'baseapp'
		@param machine: Name of machine to look at. Default all
		"""
		procs = self.getUser().getProcs()
		if machine:
			ret = [ p.pid for p in procs if p.name == processname 
					and p.machine.name == machine ]
		else:
			ret = [ p.pid for p in procs if p.name == processname ]

		return ret


	def numProxies( self ):
		"""
		Returns the number of proxies.
		"""
		return self.getUser().getNumProxies()


	# -------------------------------------------------------------------------
	# Private helpers


	def _procName( self, procType, procOrd ):
		procName = None
		if procOrd is not None:
			procName = "%s%s" % (procType, procOrd)
		else:
			procName = procType

		return procName


	def _waitForWatcher( self, procType, procOrd, path ):
		""" Waits until watcher given by path produces something other than 
			empty string and returns the value. On timeout, returns None."""


		proc = self.findProc( procType, procOrd )
		if proc is None:
			raise ClusterControllerError( "Failed to find process %s "
						"for watching" %  self._procName( procType, procOrd ) )

		pid = proc.pid

		lastMark = ""
		startTime = datetime.now()
		while (True):

			watcherData = proc.getWatcherData( path )
			if watcherData is not None:
				value = str( watcherData.value )
				if value.startswith( "pass:" ):
					lastMark = watcherData.value[5:]
					res = None
					try: 
						res = pickle.loads( lastMark )
					except:
						import traceback
						traceback.print_exc()
					return res
				if value.startswith( "fail:" ):
					lastMark = value[5:]
					failMsg = "Failed on %s: %s" % \
							( self._procName( procType, procOrd ), lastMark )
					raise TestCase.failureException( failMsg )
				if value.startswith( "mark:" ):
					lastMark = value[5:]

			currTime = datetime.now()
			if (currTime - startTime).seconds > self._timeout:
				raise ClusterControllerError( "waitForWatcher timed out " + \
							"on %s: %s" % \
							( self._procName( procType, procOrd ), lastMark ) )

			time.sleep( 1 )


	def _setupPaths( self, resPaths ):

		log.info( "ClusterControl: _setupPaths: %s" % resPaths )

		pathList = None

		if isinstance( resPaths, basestring ):
			pathList = [ resPaths ]
		else:
			pathList = resPaths


		pathBase = config.TEST_ROOT + "/res_trees/"
		relativeResPathList = [ pathBase + path 
					for path in pathList if path[0] != "/" ]
		absResPathList = [ path 
					for path in pathList if path[0] == "/" ]

		self._tempTree = pathBase + "temp_" + self.user

		log.info( "Cleaning out out '%s'" % ( self._tempTree, ) )
		try:
			command.remove( self._tempTree, )
			command.mkdir( self._tempTree )
		except command.CommandError:
			import traceback
			traceback.print_exc()
		userConfigSrc = config.TEST_ROOT + "/user_config/server/bw_" + \
							self.user + ".xml"

		userConfigDst = self._tempTree + "/server/bw_" + \
							self.user + ".xml"

		log.info( "Copying file '%s' to '%s'" 
				% ( userConfigSrc, userConfigDst ) )

		try:
			command.mkdir( os.path.split( userConfigDst )[ 0 ] )
			command.copy( userConfigSrc, userConfigDst )
			command.chmod( userConfigDst, 666 )
		except command.CommandError:
			raise ClusterControllerError( "Could not write config file '%s'" % \
											userConfigDst )

		resPaths = []
		resPaths.append( self._tempTree )
		resPaths.extend( relativeResPathList )
		resPaths.extend( absResPathList )
		resPaths.append( config.TEST_ROOT + "/helpers" )
		resPaths.append( config.CLUSTER_BW_ROOT + 
						 "/%s/res/bigworld" % config.BIGWORLD_FOLDER )

		binPath = config.CLUSTER_BW_ROOT

		log.info( "ClusterController: Setting cluster paths to %s" % resPaths )

		bwmachined_conf.setTestConfig( "%s/%s/.." % 
									  (binPath, config.BIGWORLD_FOLDER),
									  resPaths, self.user )
		config.CLUSTER_BW_RES_PATH = ":".join( resPaths )


		log.info( "ClusterControl: calling resetChain with user %s" 
				% self.user )

		bwconfig.resetChain( self.user )

		self._resPaths = resPaths

		self._coredumpsPath = os.path.join( binPath, config.BIGWORLD_FOLDER, 
										config.SERVER_BINARY_FOLDER )

		self._lastCoreDumpList = self._getCoreDumps()  


	def _getCoreDumps( self ):
		coreDumps = []
		for f in os.listdir( self._coredumpsPath ):
			path = os.path.join( self._coredumpsPath, f )
			if os.path.isdir( f ):
				continue
			if f.startswith( "core." ) or f.startswith( "assert." ):
				coreDumps.append( path )
		return coreDumps


	def _checkForCoreDumps( self, expectedFailures = None ):
		currDumps = self._getCoreDumps()
		diff = list( set( currDumps ) - set( self._lastCoreDumpList ) )
		self._lastCoreDumpList = currDumps

		if not self._enableCoreDumpChecking or not diff:
			return []

		dumpList = ' '.join( diff )

		# Do we need to print all the core dump paths in full?
		# log.error( "ClusterController: found new core dumps: %s", dumpList )

		# Now copy core dumps into a dedicated place

		snapshotDirName = time.strftime("core-snapshot-%Y%m%d-%H%M%S")
		snapshotPath = self._coredumpsPath + os.sep + snapshotDirName
		try:
			command.mkdir( snapshotPath )
		except command.CommandError:
			pass
		

		appList = []
		for dump in diff:
			head, tail = os.path.split( dump )
			traits = tail.split( '.' )
			binName = None
			if len( traits ) > 2:
				if traits[0] == "assert" or traits[0] == "core":
					binName = traits[1]

			if binName is None: 			
				log.error( "ClusterController: core dump file %s "
							"has incorrect name format", dump )
				continue
			
			if traits[-1] != "log":
				appList.append( binName )

			if expectedFailures and binName in expectedFailures:
				continue
			
			machineName = traits[2]
			outFileName = os.path.join(snapshotPath, "%s.info" % machineName )
			if not os.path.exists( outFileName ):
				outFile = command.MultiUserWriter( outFileName )
				outFile.writelines( self._getMachineInfo( machineName ) )
				outFile.close()
			binFrom = os.path.join(self._coredumpsPath, "commands", binName)
			if not os.path.exists( binFrom ):
				binFrom = self._coredumpsPath + os.sep + binName
			binTo = snapshotPath + os.sep + binName 

			

			try:
				if not os.path.exists( binTo ):
					command.copy( binFrom, binTo )
			except command.CommandError:
				log.error( "ClusterController: failed to copy %s "
							"binary into %s", binFrom, snapshotPath + os.sep )

			dumpTo = snapshotPath + os.sep + tail

			try:
				command.copy( dump, dumpTo )
			except command.CommandError:
				log.error( "ClusterController: failed to copy %s "
							"core dump into %s", dump, snapshotPath + os.sep )
		
		
		if expectedFailures and sets.Set( appList ) == sets.Set(expectedFailures):
			command.remove( snapshotPath )
		elif self.messageLogger:
			lastServerLogOutput = self.messageLogger.mlcat()
			outFile = command.MultiUserWriter( 
									os.path.join(snapshotPath, "server.log") )
			outFile.writelines( lastServerLogOutput )
			outFile.close()
		
		return appList

	def machineExists( self, machineName ):
		"""Checks if a specific machine name is found in the cluster
		@param machineName: Machine to look for
		"""
		env = command_util.CommandEnvironment( self.user )
		machines = env.getSelectedMachines( [machineName] )
		return len(machines) > 0
		
	def _getMachineInfo( self, machineName ):
		env = command_util.CommandEnvironment( self.user )
		machines = env.getSelectedMachines( [machineName] )
		ret = ""
		for machine in machines:
			ret += str(machine)
			ret += "\n"
			for ifname, stats in sorted( machine.ifStats.items() ):
				if stats is not None:
					ret += "\t%s\n" % stats
			ret += "\tloss: %d/%d\n" % (machine.inDiscards, machine.outDiscards)
		return ret
	
class Bots( object ):
	"""
	This class is a helper for ClusterController to interact with the bots
	process. An instance of this class can be accessed via bots member of
	ClusterController instance
	"""

	NBOTS_AT_ONCE = 20
	SLEEP_BETWEEN_ADDING = 2

	def __init__( self, parent ):
		"""Constructor.
		@param parent: ClusterController instance
		"""
		self._parent = parent


	def getUser( self ):
		"""Returns the user object from pycommon.
		"""
		return self._parent.getUser()


	def add( self, numBots, timeout = 20 ):
		"""Add bots.
		This method doesn't guarantee we add the required number of bots.
		It's our best effort to add them, but Bots.numBots() should
		be used as a reliable way to get the actual number of bots
		@param numBots: Number of bots to add
		@param timeout: Time to wait before triggering error. Default 20s
		"""
		self.getUser().addBots( numBots, timeout )


	def addWithCredentials( self, username, password = None ):
		"""Add a bot using the specified credentials.
		@param username: username to use for the bot
		@param password: 
		"""
		oldUsernameValue = self._parent.getWatcherValue( 
										"config/username", "bots", None )
		oldPasswordValue = self._parent.getWatcherValue( 
										"config/password", "bots", None )
		oldShouldUseRandom = self._parent.getWatcherValue( 
									"config/shouldUseRandomName", "bots", None )
		self._parent.setWatcher( "config/username", username, "bots", None )
		self._parent.setWatcher( "config/password", password, "bots", None )
		self._parent.setWatcher( 
						"config/shouldUseRandomName", "False", "bots", None )
		time.sleep( 2 )
		self.getUser().addBots( 1, 5 )
		time.sleep( 2 )
		self._parent.setWatcher( 
							"config/username", oldUsernameValue, "bots", None )
		self._parent.setWatcher( 
							"config/password", oldPasswordValue, "bots", None )
		self._parent.setWatcher( "config/shouldUseRandomName", 
								oldShouldUseRandom, "bots", None )
	
	def delete( self, numBots, timeout = 20 ):
		"""Delete bots.
		This method doesn't guarantee we delete the required number of bots.
		It's our best effort to add them, but Bots.numBots() should
		be used as a reliable way to get the actual number of bots
		@param numBots: Number of bots to add
		@param timeout: Time to wait before triggering error. Default 20s
		"""
		self.getUser().delBots( numBots, timeout )


	def setMovement( self, controllerType, controllerData, botTag = "Default" ):
		"""Set movement algorithm for a specific bot
		@param controllerType: Type of movement eg. Beeline, Patrol
		@param controllerData: String of data a specific controller expects
		@param botTag: String tag representing a group of bots. Default "Default"
		"""
		self.getUser().setBotMovement( controllerType, controllerData, botTag )


	def load( self ):
		"""Returns a list of load values for each bot process.
		"""
		return [p.load for p in self.procs()]


	def numBots( self ):
		"""Returns the number of bots currently running.
		"""
		self.getUser().cluster.refresh()
		return sum( [p.nbots() for p in self.procs()] )


	def procs( self ):
		"""Returns the process objects of currently running bots processes
		"""
		return self.getUser().getProcs( "bots" )

# cluster.py
