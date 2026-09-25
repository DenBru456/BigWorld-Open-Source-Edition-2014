#!/usr/bin/env python

import fnmatch
import random
import re

import sys
import os
import logging
sys.path.append( os.path.dirname( __file__ ) + "/../.." )

from pycommon import cluster
from pycommon import process as process_module
from cluster_constants import BW_CONFIG_HYBRID

log = logging.getLogger( __name__ )


def selectMachines( cluster, args ):

	if not args or args == ["all"]:
		return cluster.getMachines()

	machines = set()

	for a in args:

		# Catch glob() patterns
		if re.search( "[\*\?\[]", a ):
			found = False
			for m in cluster.getMachinesIter():
				if fnmatch.fnmatch( m.name, a ):
					machines.add( m )
					found = True

			if not found:
				log.error( "No machines match pattern '%s'", a )
				return []

		# Catch version:n
		elif a.startswith( "version:" ):
			version = int( a.split( ":" )[1] )
			for m in cluster.getMachinesIter():
				if m.machinedVersion == version:
					machines.add( m )

		# Catch group:g
		elif a.startswith( "group:" ):
			group = a.split( ":" )[1]
			cluster.queryTags( "Groups" )
			found = False
			for m in cluster.getMachinesIter():
				if "Groups" in m.tags and group in m.tags[ "Groups" ]:
					machines.add( m )
					found = True

			if not found:
				log.error( "No machines in group '%s'", group )
				return []

		# Catch :noprocs:
		elif a == ":noprocs:":
			for m in cluster.getMachinesIter():
				if not m.getProcs():
					machines.add( m )

		# Catch :best:
		elif a == ":best:":
			ms = filter( lambda m: not m.getProcs(), cluster.getMachines() )
			if not ms:
				log.error( "All machines are running at least one process" )
				continue

			# Reverse-sort list by CPU speed
			ms.sort( key = lambda m: -m.totalmhz() )

			# Stably sort list by load
			ms.sort( key = lambda m: m.load() / m.totalmhz() )
			machines.add( ms[0] )

		# Must be an exact hostname or IP address now
		else:
			m = cluster.getMachine( a )
			if m:
				machines.add( m )
			else:
				log.error( "Unknown machine: %s", a )
				return []

	return sorted( machines )


def selectProcesses( user, processTypes ):

	procs = set()

	for procType in processTypes:
		a = procType.lower()

		if a != procType:
			log.info( "Using '%s' instead of '%s'", a, procType )

		# Catch 'cellapp1', so 'cellapp{1..5}' brace expansion will work :)
		m = re.match( "([a-z]+)(\d)$", a )
		if m:
			p = user.getProcExact( "%s%02d" % (m.group(1), int( m.group(2) ) ) )
			if p:
				procs.add( p )
				continue
			else:
				log.error( "No process matching '%s'", a )
				return None

		# Catch 'cellapp01' and 'bots:bwdev13:4315'
		if re.match( "[a-z]+\d\d+$", a ) or a.startswith( "bots:" ):
			p = user.getProcExact( a )
			if p:
				procs.add( p )
				continue
			else:
				log.error( "No process matching '%s'", a )
				return None

		# Catch multiapp plurals e.g. 'cellapps'
		if re.match( "(cellapps|baseapps|loginapps|serviceapps|bots|dbapps)",
				a ):
			if a == "bots":
				ps = user.getProcs( a )
			else:
				ps = user.getProcs( a[:-1] )
			if ps:
				procs.update( ps )
				continue
			else:
				log.error( "No process matching '%s'", a )
				return None

		# Catch singleton processes
		if a in process_module.Process.types.startable():
			ps = user.getProcs( a )
			if ps:
				procs.add( random.choice( ps ) )
				continue
			else:
				log.error( "No process matching '%s'", a )
				return None

		# Catch machine:PID
		m = re.match( "([\w-]+):(\d+)", a )
		if m:
			machine = user.cluster.getMachine( m.group( 1 ) )
			if not machine:
				log.error( "Unknown machine: %s", m.group( 1 ) )
				return None

			pid = int( m.group( 2 ) )
			p = machine.getProc( pid )
			if p:
				procs.add( p )
				continue
			else:
				log.error( "No process with PID %d on %s", pid, machine.name )
				return None

		# Catch 'all'
		if a == "all":
			procs.update( [ p for p in user.getProcs() if p.name != "message_logger" ] )
			continue

		log.error( "No process matching '%s'", a )
		return None

	return sorted( procs )


def isServerRunning( user ):
	# Currently fall back to old method if new method didn't work.
	loginApps = user.getProcs( "loginapp" )

	if (loginApps and loginApps[0].statusCheck()) or \
			user.serverIsRunning():
		return True
	else:
		return False


def startProcess( cluster, user, processName, machineNames, num,
					bwConfig = BW_CONFIG_HYBRID ):

	status = True
	machinesList = selectMachines( cluster, machineNames )

	if (machinesList == None) or (len( machinesList ) == 0):
		status = False

	if status == True:

		for machine in machinesList:
			status = user.startProc( machine, processName, num,
									bwConfig = bwConfig ) and status

	return status


# Search all methods of the specified appType to see if they own the entity
def findProcessWithEntity( user, appType, entityID ):

	processWithEntity = None
	for process in user.getProcs( appType ):
		log.info( "Scanning %s ...", process.label() )

		watcherData = process.getWatcherData( "entities" )
		for entry in watcherData:
			try:
				eid = int( entry.name )
			except ValueError:
				continue

			if eid == entityID:
				processWithEntity = process

	return processWithEntity


class CommandEnvironment( object ):
	def __init__( self, uid = None, isVerbose = False, machine = None ):
		self._uid = uid
		self.isVerbose = isVerbose
		self.machine = machine


	def getCluster( self, shouldRetrievePlatformInfo = False ):
		if not hasattr( self, '_cluster' ):
			import cluster
			self._cluster = cluster.cache.get( uid = None,
						shouldRetrievePlatformInfo = shouldRetrievePlatformInfo )

		return self._cluster


	def getUser( self, checkCoreDumps = False, refreshEnv = False,
				fetchVersion = False, machine = None ):
		if not hasattr( self, '_user' ):
			if self.machine is not None:
				self.machine = self.getCluster().getMachine( self.machine )

			# use the passedin machine if specified
			if machine is None:
				machine = self.machine

			# uidmodule.getuid() is a cluster query, so delay it until needed
			import uid as uidmodule
			self._user = self.getCluster().getUser(
				uid = uidmodule.getuid( self._uid ),
				machine = machine,
				refreshEnv = refreshEnv,
				checkCoreDumps = checkCoreDumps,
				fetchVersion = fetchVersion )

		return self._user


	def getSelectedProcesses( self, processList ):
		user = self.getUser()
		return selectProcesses( user, processList )


	def getSelectedMachines( self, machineList,
							shouldRetrievePlatformInfo = False ):
		return selectMachines( self.getCluster( shouldRetrievePlatformInfo ),
								machineList )

	def debug( self, *args, **kw ):
		return log.debug( *args, **kw )

	def info( self, *args, **kw ):
		return log.info( *args, **kw )

	def warning( self, *args, **kw ):
		return log.warning( *args, **kw )

	def error( self, *args, **kw ):
		return log.error( *args, **kw )

	def critical( self, *args, **kw ):
		return log.critical( *args, **kw )

	def usageError( self, errorMsg, usageFn ):
		self.error( errorMsg )
		self.info( "Usage: " + usageFn() )
		return False

def runCommand( runFunc, args = None ):
	if args is None:
		import sys
		args = sys.argv[1:]

	if runFunc( args, CommandEnvironment() ):
		return 0
	else:
	 	return 1


def genericServerStart( env, machines=[], startBots=False, startRevivers=False, 
		obeyBWmachinedTags=True, useSimpleLayout = False,
		getUsageStr = lambda : "No usage string available",
		bwConfig = BW_CONFIG_HYBRID ):

	status = True

	if not machines:
		return env.usageError( "You must pass 'all' to start the server "
				   "on all available machines",
				getUsageStr )

	cluster = env.getCluster()
	selectedMachines = selectMachines( cluster, machines )

	if not selectedMachines:
		status = False
	else:
		
		if len( selectedMachines ) == 1:
			user = env.getUser(	refreshEnv = True, fetchVersion = True,
						machine = selectedMachines[0] )
		else:
			user = env.getUser( refreshEnv = True, fetchVersion = True )

		status = user.start( selectedMachines,
			bots = startBots,
			revivers = startRevivers,
			tags = obeyBWmachinedTags,
			useSimpleLayout = useSimpleLayout,
			bwConfig = bwConfig )

	return status

# command_util.py
