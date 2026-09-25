import operator
import itertools
import threading
import time
import sys
import Queue
import logging
import traceback
import math

# Import pycommon modules
import bwsetup
bwsetup.addPath( ".." )
from pycommon.watcher_data_message import WatcherDataMessage
from pycommon import cluster
from pycommon import user as user_module

import constants

from model.db_store import DbStore


# Logging module
log = logging.getLogger( __name__ )


class StatGatherer( threading.Thread ):
	""" Thread for gathering statistics.  """
	FINISH = 0
	START_DEBUG = 1

	def __init__( self, sampleTickInterval, usingFileOutput, prefTree, 
				uid = None):
		threading.Thread.__init__( self, name="StatGatherer" )

		# Set to true if profiling StatGatherer thread
		self.profiling = False

		# Update interval, pulled from options file
		self.sampleTickInterval = sampleTickInterval

		# Don't print the tick rotater if we're logging to a file
		self.usingFileOutput = usingFileOutput
		
		# Preference tree containing all preferences (important!)
		self.prefTree = prefTree

		# Cluster object (from pycommon) which does the heavyweight work
		if uid:
			self.cluster = cluster.Cluster( uid = uid )
		else:
			self.cluster = cluster.Cluster()
		# Flush cluster information in periodically
		self.reflushClusterPeriodSecs = 3600
		# The last time flush cluster information
		self.lastReflushClusterTime = time.time()

		#  Message queue for handling messages from the main thread
		self.messageQueue = Queue.Queue()

		# Machine statistics: [Machine object] -> [Statistics]
		self.machineStats = {}
		self.missingMachines = set()

		# Machine statistics: [Process object] -> [Statistics]
		self.processStats = {}
		self.missingProcesses = set()

		# Set of processes that aren't responding to watcher queries
		self.deadProcs = {}

		# Set of User objects
		self.userStats = set()

		# Some statPrefs require lambdas to be created
		self.compiledStatFuncs = {}	

		# Map of ProcPref.matchtext -> {ProcPref -> watcherValue}
		self.watcherStatPrefs = self.getWatcherStatPrefs( self.prefTree )

		# Map of Process.name -> ProcPref
		self.nameToProcPref = \
			dict( (pref.matchtext, pref) for pref in \
				self.prefTree.iterProcPrefs() )

		# Daemon log mark output period. Mark every hour.
		self.markPeriodSecs = 3600
		# The last time we printed a mark
		self.lastMarkOutputTime = time.time()		

		# Guard against having the computer clock set backwards
		self.latestKnownTime = None

		# Set when we need to terminate quickly, and ignore queued SQL
		# statements
		self.quickTerminate = False

		# This is the time at which we want the current tick to have
		# completed by.
		# NB: The initialisation is done elsewhere, added here for reference
		#self.desiredTickTime = time.time()

		# Rotating characters
		self.rotateChars = "|/-\\"
		self.rotatePos = 0

		# Sleep intervals
		self.sleepTime = 0.1
		
		# Statistic stores
		# DB store is treated a little bit specially because we need it to
		# perform some extra tasks, like retrieveLatestTime and getFirstTick
		self.dataStores = []

	class FinishException(Exception):
		pass

	# ------------------------------------------------------
	# Section: exposed communication methods
	# ------------------------------------------------------
	def pushFinish( self, quick=False ):
		"""
		Send a finish signal to this StatGatherer thread.

		@param quick: True if we should stop immediately upon receiving
			the signal (does not write pending insert statements to the
			database)
		"""
		self.messageQueue.put( (self.FINISH, quick) )
	# pushFinish

	def pushDebug( self ):
		"""
		Send a signal to the StatGatherer thread to start the debugger
		(requires winpdb).
		"""
		self.messageQueue.put( (self.START_DEBUG,None) )
	# pushDebug


	# ------------------------------------------------------
	# Section: exposed methods
	# ------------------------------------------------------		
	def addDataStore( self, dataStore ):
		self.dataStores.append( dataStore )
	# addStore


	# ------------------------------------------------------
	# Section: Internal general methods
	# ------------------------------------------------------
	def getWatcherStatPrefs( self, prefTree ):
		""" Determine which statistic preferences are watcher preferences """
		watcherStatPrefs = {}
		for procPref in prefTree.iterProcPrefs():
			# Index by matchtext, which is supposed to match the value returned
			# by Process.name.
			# This means if we have a Process object, we can
			# back reference from it to the watcherStatPref.
			watcherStatPrefs[procPref.matchtext] = dict(
				(s, s.valueAt[1:].encode( constants.STAT_LOGGER_CHARSET ))
				for s in procPref.iterAllStatPrefs()
					if self.isWatcherPath(s.valueAt) )

		return watcherStatPrefs
	# getWatcherStatPrefs


	def run( self ):
		""" Thread entry point """
		if self.profiling:
			import cProfile
			prof = cProfile.Profile()
			prof.runcall( self.runGather )
			prof.dump_stats( "stat_logger.prof" )
			log.debug( "Dumped profile statistics to stat_logger.prof" )
		else:
			self.runGather()
		log.info( "StatGatherer thread terminating normally" )
	# run


	def runGather( self ):
		""" Handle the main StatGatherer loop """				
		self.latestKnownTime = self.retrieveLatestTime()

		# Retrieve the next tick id and the time at which it should start
		self.tick, self.desiredTickTime = self.calculateStartTick()

		# If this isn't the start of the log, wait a bit so that our ticks
		# are in sync (in order to maintain regular intervals between ticks)
		if self.tick > 1:
			time.sleep( self.desiredTickTime - time.time() )

		# Delete old data. Old data may span multiple ticks, and thus the
		# amount data to delete will vary.
		self.deleteOldData()

		log.info( "StatLogger ready to collect data." )

		try:
			# Start the StatGatherer loop!
			while True:
				self.tickTime = time.time()
				if self.checkSystemClock() == False:
					# Our system clock has gone backwards?
					log.info( "Going to stop collecting data until clock " \
						"has caught up to previous maximum time. This is " \
						"about %.3fs.", time.time() - self.latestKnownTime )
					self.waitUntilTime( self.latestKnownTime )
					log.info( "Catchup complete, resuming data collection." )
					self.calculateNextTick()
					self.waitUntilTime( self.desiredTickTime )
					continue

				# Check whether need to flush cluster information
				if self.tickTime - self.lastReflushClusterTime >= self.reflushClusterPeriodSecs:
					self.cluster.refresh()
					self.lastReflushClusterTime = self.tickTime

				self.latestKnownTime = self.tickTime
				self.addTick( self.tick, self.tickTime )
				# Most important step: Collect and log data to the database
				self.collectData()
				self.consolidateStats()
				self.handlePeriodicOutput()

				self.checkStores()
				while not self.messageQueue.empty():
					self.processMessage( self.messageQueue.get(0) )

				self.calculateNextTick()
				self.waitUntilTime( self.desiredTickTime )
		except self.FinishException:
			pass

		self.finalise( self.quickTerminate )
	# runGather


	def retrieveLatestTime( self ):
		""" Grab the last tick out of the database """
		for dataStore in self.dataStores:
			if isinstance( dataStore, DbStore ):
				return dataStore.retrieveLatestTime()

		return None
	# retrieveLatestTime


	def calculateStartTick( self ):
		"""
		Calculate which tick we start gathering on and what timestamp
		that tick corresponds to
		"""
		results = None
		
		for dataStore in self.dataStores:
			if isinstance( dataStore, DbStore ):
				results = dataStore.getFirstTick()

		if results == None:
			nextTick = (1, time.time())
		else:
			firstTick, firstTickTime = results
			timeElapsed = time.time() - firstTickTime
			numTicks = timeElapsed/self.sampleTickInterval
			nextTickId = firstTick + math.ceil( numTicks )
			nextTickTime = firstTickTime + \
				(float(nextTickId) * self.sampleTickInterval)
			nextTick = (nextTickId, nextTickTime)
		return nextTick
	# calculateStartTick


	def deleteOldData( self ):
		""" Delete old data that may span multiple ticks.  The amount of data to
			delete varies.  This is performed only on StatLogger startup. """
		log.info( "Performing maintenance task...This may take a while." )
		# Uses deletion code in consolidateStats method.  No consolidation is
		# performed.
		self.consolidateStats( False )
		log.info( "Finished performing maintenance task." )
	# deleteOldData


	def checkSystemClock( self ):
		""" Check that the system clock hasn't been set backwards """
		if self.tickTime < self.latestKnownTime:
			log.warning( "Current time %s is lower than maximum recorded " \
				"time of %s (difference of %.3fs)",
				time.ctime( self.tickTime ),
				time.ctime( self.latestKnownTime ),
				self.latestKnownTime - self.tickTime )
			log.warning( "Has the computer's clock been set backwards?" )
			return False
		return True
	# checkSystemClock


	def waitUntilTime( self, targetTime):
		""" Process messages until the target time is reached """
		if time.time() > targetTime:
			return
		checkUntil = targetTime - 2 * self.sleepTime
		while time.time() < checkUntil:
			try:
				self.processMessage( self.messageQueue.get(0) )
			except Queue.Empty:
				pass
			time.sleep( self.sleepTime )
		timeRemaining = targetTime - time.time()
		if timeRemaining > 0:
			time.sleep( timeRemaining )
		else:
			log.warning( "We slept overtime by %.3fs :(", timeRemaining )
	# waitUntilTime


	def calculateNextTick( self ):
		""" Calculates when the next tick should start """
		self.tick += 1
		self.desiredTickTime += self.sampleTickInterval

		# If we've gone overtime...then "skip" ticks
		currTime = time.time()
		timeRemaining = self.desiredTickTime - currTime
		multiTimeCorrection = False

		while timeRemaining < 0:

			# Skip the number of ticks that we've missed
			ticksMissed = math.ceil(
				(-timeRemaining) / self.sampleTickInterval )
			self.tick += ticksMissed

			# Recalculate the new desired tick finish time based on the
			# number of ticks we're skipping
			self.desiredTickTime += ticksMissed * self.sampleTickInterval

			log.warning( "Last tick went overtime by %fs. " \
				"Waiting %fs for tick %d (skipping %d)",
				-timeRemaining, self.desiredTickTime - currTime, self.tick,
				ticksMissed )

			# Make sure the generated state to progress to is valid
			timeRemaining = self.desiredTickTime - currTime
			if (timeRemaining < 0):
				log.error( "Failed to recover from exceeding previous tick " \
					"time allocation." )

				if multiTimeCorrection == True:
					log.error( "Failed to correct time sync. Terminating." )
					raise self.FinishException()

				multiTimeCorrection = True
	# calculateNextTick


	def processMessage( self, messageTuple ):
		""" Handles messages passed to us from the main thread """
		msg, params = messageTuple
		if msg == self.START_DEBUG:
			import rpdb2
			pauseTime = 15
			log.info( "Waiting %ds for debugger to connect", pauseTime )
			rpdb2.start_embedded_debugger(
				"abcd",
				fAllowUnencrypted = True,
				fAllowRemote = True,
				timeout = pauseTime,
				fDebug = False )
		elif msg == self.FINISH:
			log.info( "Stopping data collection (Current tick is %i)." \
				% self.tick )
			self.quickTerminate = params
			raise self.FinishException()
	# processMessage


	def handlePeriodicOutput( self ):
		""" Handles output that we're expected to make at regular intervals """
		if self.usingFileOutput:
			if time.time() - self.lastMarkOutputTime > self.markPeriodSecs:
				log.info( "-- MARK --" )
				self.lastMarkOutputTime = time.time()
		else:
			# Assume stdout output
			sys.stdout.write( "%c\r" % (self.rotateChars[self.rotatePos]) )
			sys.stdout.flush()
			self.rotatePos = (self.rotatePos + 1) % len( self.rotateChars )
	# handlePeriodicOutput


	def checkStores( self ):
		""" Check Stores' status """
		for dataStore in self.dataStores:
			if not dataStore.isOk():
				raise self.FinishException()
	# checkStores


	def finalise( self, quickTerminate = True ):
		for dataStore in self.dataStores:
			dataStore.finalise( quickTerminate )
	# finalise


	def isWatcherPath( self, value ):
		return value[0] == "/"
	# isWatcherPath


	# ------------------------------------------------------
	# Section: Statistic collection methods
	# ------------------------------------------------------
	def collectData( self ):
		"""
		Collects data from machines and process on the network,
		and logs them to the database.
		"""
		# Refresh cluster, this is the most important operation for
		# collecting statistics
		try:
			self.cluster.refresh( 1 )
		except:
			log.error( traceback.format_exc() )

		# Extracts statistics from cluster
		self.extractMachineStats()
		self.extractProcessStats()
		self.extractUserStats()
		self.checkDeadProcessesAndMachines()
		self.logProcessStats()
		self.logMachineStats()
	# collectData


	def extractUserStats(self):
		""" Manage users detected on the network """
		users = self.cluster.getUsers()
		for u in users:
			if u not in self.userStats:
				self.logNewUser(u)
	# extractUserStats


	def extractMachineStats( self ):
		""" Manage stats from machines detected on the network """
		machines = self.cluster.getMachines()
		lastKnownMachines = set(self.machineStats)
		for m in machines:
			if m not in lastKnownMachines:
				# Log a machine if it wasn't there before
				self.logNewMachine(m)
				self.machineStats[m] = {}
			else:
				lastKnownMachines.remove(m)
			assert (not self.machineStats[m])
			self.machineStats[m] = dict( (pref, self.applyStatFunc(m, pref) )
				for pref in self.prefTree.iterMachineStatPrefs() )

		# This is the set of machines that have disappeared from the network
		self.missingMachines = lastKnownMachines
	# extractMachineStats


	def extractProcessStats( self ):
		"""
		Retrieve stats for processes detected on the network.
		First get the stats which access attributes of the Process
		object, then after all that is done get the watcher stats.
		"""
		lastKnownProcs = set(self.processStats)
		availableProcs = (p for p in self.cluster.getProcs() if \
			p.name in self.nameToProcPref)
		for p in availableProcs:
			procPref = self.nameToProcPref[p.name]
			if p not in lastKnownProcs:
				self.logNewProcess(p)
				self.processStats[p] = {}
			else:
				lastKnownProcs.remove(p)
			assert (not self.processStats[p])

			# Retrieve non-watcher stats for the process
			nonWatcherPrefs = (pref for pref in procPref.iterAllStatPrefs() \
				if not self.isWatcherPath( pref.valueAt ))

			for pref in nonWatcherPrefs:
				self.processStats[p][pref] = self.applyStatFunc( p, pref )

		# Now, get watcher values for all processes
		self.retrieveWatcherValues()

		# This is the set of processes that have disappeared from the network
		self.missingProcesses = lastKnownProcs
	# extractProcessStats


	def applyStatFunc( self, obj, statPref ):
		"""
		Applies the function specified in the valueAt attribute of each
		statistic preference to the actual Process or Machine object.
		"""
		try:
			func = self.compiledStatFuncs[statPref.valueAt]
		except KeyError:
			func = eval("lambda m: m." + statPref.valueAt)
			self.compiledStatFuncs[statPref.valueAt] = func

		try:
			result = func( obj )
		except IndexError:
			return 0.0
		except KeyError:
			return 0.0
		return result
	# applyStatFunc


	def retrieveWatcherValues( self ):
		"""
		Retrieves watcher values for all processes that we've detected
		on the network. This is a blocking operation, and can take some time.
		"""
		# Create dictionary of {processType -> [processes])
		getName = operator.attrgetter('name')
		processes = sorted( (p for p in self.cluster.getProcs() \
			if p.name in self.nameToProcPref), key=getName )
		groupedProcesses = itertools.groupby( processes, getName )

		# The number of times to attempt to query a process when
		# it's not replying to watcher queries.
		DEAD_ATTEMPTS = 3

		# Iterate through all process types
		for procType, processList in groupedProcesses:
			multiProcWatcherPaths = self.watcherStatPrefs[procType].values()
			
			# Build list of watcher paths for which only one proc should be 
			# queried and delete from the multi-proc list
			singleProcWatcherPaths = []
			for pref, path in self.watcherStatPrefs[procType].iteritems():
				if pref.fetchFromSingleInstance:
					del multiProcWatcherPaths[multiProcWatcherPaths.index( path )]
					singleProcWatcherPaths.append( path )
					
			if len(multiProcWatcherPaths) == 0 and len(singleProcWatcherPaths) == 0:
				continue

			# Check every process we are told about to see whether we
			# have already queried them before and determined they are
			# 'dead' or are talking an older protocol.
			newProcList = []
			for queryProc in processList:
				putInList = True
				for deadProc in self.deadProcs.keys():
					if (self.deadProcs[ deadProc ])[0] >= DEAD_ATTEMPTS:
						if (queryProc.id == deadProc.id) and \
							(queryProc.pid == deadProc.pid) and \
							(queryProc.uid == deadProc.uid) and \
							(queryProc.machine == deadProc.machine):

							# Every 5 minutes give the process another chance
							if (self.tickTime - (self.deadProcs[ deadProc ])[1]) > 300:
								# Remove from the dead list
								log.info( "5 minute timeout for (%s on %s " \
									"pid:%s). Removing from dead list.",
									deadProc.name, deadProc.machine.name,
									deadProc.pid )
								self.deadProcs.pop( deadProc )

							putInList = False
							break

				# Put it in the list to query unless told otherwise
				if putInList:
					newProcList.append( queryProc )


			try:
				watcherResponse = WatcherDataMessage.batchQuery(
					multiProcWatcherPaths, newProcList, 0.5 )

				# Fetch from a single proc and merge into multi-proc response
				if singleProcWatcherPaths:
					singleProcResponse = WatcherDataMessage.batchQuery(
						singleProcWatcherPaths, [newProcList[0]], 0.5 )
					for p, watcherReply in singleProcResponse.iteritems():
						watcherResponse[p].update( watcherReply )

			except Exception, e:
				log.error( "Watcher query failed. Dropping all current " \
					"statistic requests. Exception follows:\n" )
				log.error( str(e) )
				for msg in traceback.format_tb(sys.exc_info()[2]):
					log.error("%s", msg)

				continue


			# Process watcher response for processes in a process type
			for p, watcherReplyDict in watcherResponse.iteritems():
				if not len(watcherReplyDict):

					entry = None
					if p in self.deadProcs:
						entry = self.deadProcs[ p ]
					else:
						entry = ( 0, self.tickTime )

					if entry[0] < DEAD_ATTEMPTS:
						self.deadProcs[ p ] = ( entry[0] + 1, entry[1] )

					# no need to do anything else with this process
					continue

				elif self.deadProcs.has_key( p ):
					# Remove from the dead list
					self.deadProcs.pop( p )
					log.info( "Removing %s on %s pid:%s from dead list, " \
						"responding again.", deadProc.name,
						deadProc.machine.name, deadProc.pid )

				for statPref, watcherPath in \
						self.watcherStatPrefs[p.name].iteritems():
					replies = watcherReplyDict.get(watcherPath,None)
					if replies:
						if len(replies) > 1:
							log.warning( "Watcher request %s to %s " \
								"resulted in multiple replies. Possible "\
								"delayed watcher response to earlier query. ",
								watcherPath, p)
						self.processStats[p][statPref] = replies[-1][1]
					else:
						self.processStats[p][statPref] = None
	# retrieveWatcherValues


	def checkDeadProcessesAndMachines( self ):
		"""
		Handles processes and machines which have been lost
		(either shutdown, crashed, or lost network access)
		"""
		for machine in self.missingMachines:
			log.info( "Lost machine %s (%s)", machine.name, machine.ip )
			del self.machineStats[machine]

		for process in self.missingProcesses:
			try:
				user = self.cluster.getUser( process.uid ).name
			except user_module.UserError, e:
				log.warning(e)
				user = process.uid
			log.info( "Lost process %s(user:%s, pid:%d, host:%s)",
				process.label(), user, process.pid,
				process.machine.name )
			del self.processStats[process]
			self.removeActiveProcess( process )
			
		self.missingProcesses.clear()
		self.missingMachines.clear()
	# checkDeadProcessesAndMachines


	def removeActiveProcess( self, process ):
		for dataStore in self.dataStores:
			dataStore.delProcess( process )
	# removeActiveProcess


	# ------------------------------------------------------
	# Section: Logging methods
	# ------------------------------------------------------

	def logNewMachine( self, machine ):
		""" Adds machine info to the dataStore if it doesn't already exist """
		for dataStore in self.dataStores:
			dataStore.logNewMachine( machine )
	# logNewMachine


	def logNewProcess( self, process ):
		""" Adds process info to the dataStore if it doesn't already exist """
		if process.name not in self.nameToProcPref:
			return

		try:
			userName = self.cluster.getUser( process.uid ).name
		except user_module.UserError:
			userName = "<%d>" % process.uid

		for dataStore in self.dataStores:
			dataStore.logNewProcess( process, userName )
	# logNewProcess


	def logNewUser(self, user):
		""" Adds user info to the dataStore if it doesn't already exist """
		for dataStore in self.dataStores:
			dataStore.logNewUser( user )
	# logNewUser


	def logMachineStats( self ):
		""" Logs stats for all machines """
		for dataStore in self.dataStores:
			dataStore.logMachineStats( self.machineStats, self.tick )

		# Empty the stats, we don't need it anymore
		for m, statDict in self.machineStats.iteritems():
			statDict.clear()
	# logMachineStats


	def logProcessStats( self ):
		""" Logs stats for all processes """
		for dataStore in self.dataStores:
			dataStore.logProcessStats( self.processStats, self.tick )			

		# Empty the stats, we don't need it anymore
		for process, statDict in self.processStats.items():
			statDict.clear()
	# logProcessStats


	def consolidateStats( self, shouldLimitDeletion=True ):
		for dataStore in self.dataStores:
			dataStore.consolidateStats( self.tick, shouldLimitDeletion )
	# consolidateStats


	def addTick( self, tick, tickTime ):
		for dataStore in self.dataStores:
			dataStore.addTick( tick, tickTime )
	# addTick


# StatGatherer.py
