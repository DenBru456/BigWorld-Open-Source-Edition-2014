import BigWorld
from bwdebug import *
import os
import ResMgr
import FDConfig
import GarbageCollectionDebug
import TradingSupervisor
import AuctionHouse
import HierarchyCheck
from GameData import FantasyDemoData

# This is imported here to avoid loading in the main thread.
import UserDataObjectRef

import NoteDataStore

import xmpp.Service as XMPPService
import XMPPEventNotifier

import gc
import pprint
import logging

try:
	# srvtest is optional
	# It will only be used if we run Fantasydemo from the testing environment
	import srvtest
except ImportError:
	pass

log = logging.getLogger( "BWPersonality" )
xmppLog = logging.getLogger( "XMPP" )
noteStoreLog = logging.getLogger( "NoteStore" )

NOTE_STORE_CONFIG = "server/config/note_data_store.xml"
XMPP_CONFIG = "server/config/xmpp.xml"
DO_GC_DUMP = False

# ------------------------------------------------------------------------------
# Section: Callbacks
# ------------------------------------------------------------------------------

def onInit( isReload ):
	""" Callback function when scripts are loaded. """

	# Check that the entitydef inheritance hierarchy strictly
	# matches the Python class hierarchy.

	# HierarchyCheck.checkTypes()

	if NoteDataStore.init( NOTE_STORE_CONFIG ):
		noteStoreLog.info( "Note Data Store example enabled" )
	else:
		noteStoreLog.info( "Note Data Store example disabled" )

	deferredXMPPInit = XMPPService.init( XMPP_CONFIG )

	def initCallback( ( result, failureReason ) ):
		if result:
			xmppLog.info( "XMPP Chat example enabled" )
		else:
			xmppLog.info( "XMPP Chat example disabled (%s)", failureReason )

		log.trace( "onInitCallback finished" )

	deferredXMPPInit.addCallbacks( initCallback )

def onFini():

	# Need to name file so that it doesn't overwrite the cell's log
	# There can be multiple cellapps running so name by PID as well
	pid = os.getpid()
	hostname = os.uname()[ 1 ]
	numLeaks = GarbageCollectionDebug.gcDump( DO_GC_DUMP,
		"gcDump.base.%s.%d.log" % ( hostname, pid ) )

	if numLeaks > 0:
		DEBUG_MSG( "FantasyDemo.onFini: Potential circular references" )
		DEBUG_MSG( "Number of leaks:", numLeaks )

	# We also run fini here in case it isn't a controlled shutdown. This helps
	# avoid the BaseApp failing to shutdown cleanly due to a race condition
	# with thread startup and shutdown. We still perform regular shutdown in
	# onAppShutDown as that allows the NoteDataStore subsystem to cleanly 
	# terminate.
	NoteDataStore.fini()


def onAppReady( isBootstrap, didAutoLoadEntitiesFromDB ):
	# Load all the runscript watchers for this baseapp

	log.trace( "onAppReady isBootstrap: %s", str( isBootstrap ) )

	if not isBootstrap:
		return

	if didAutoLoadEntitiesFromDB:
		INFO_MSG( "Bootstrap: auto-loaded entities from DB" )

	else:
		INFO_MSG( "Bootstrap: did not autoload entities from DB" )
		TradingSupervisor.wakeupTradingSupervisor()
		AuctionHouse.wakeup()

		# create space loader for each space
		for realmID, realm in FantasyDemoData.REALMS.iteritems():
			# The first space in a realm is considered the default space.
			# Players will initially be created here.
			isDefault = True

			for space in realm.spaces:
				entity = BigWorld.createBaseLocally( "SpaceLoader",
							spaceDir = space.path,
							isDefault = isDefault,
							realm = realmID,
							wasAutoLoaded = False,
							startPosition = space.startPosition )
				isDefault = False

	deferredXMPPIsEnabled = XMPPService.isEnabled()

	def enabledCallback( isEnabled ):
		if isEnabled:
			XMPPEventNotifier.wakeupXMPPEventNotifier()

	deferredXMPPIsEnabled.addCallback( enabledCallback )


def onAppShutDown( state ):
	if state == 0:
		XMPPEventNotifier.destroyXMPPEventNotifier()
		NoteDataStore.fini()


def onCellAppDeath( addr ):
	XMPPEventNotifier.broadcast( "CellApp %s died" % addr )

# ------------------------------------------------------------------------------
# Section: Common base class
# ------------------------------------------------------------------------------

class Base( BigWorld.Base ):
	def __init__( self ):
		BigWorld.Base.__init__( self )

		# This is useful if using disaster recovery.
		# if not self.databaseID:
		#	self.writeToDB()

		if hasattr( self, "cellData" ):
			try:
				cell = self.createOnCell
				self.createOnCell = None
			except AttributeError, e:
				cell = None

			if cell != None:
				self.createCellEntity( cell )
			elif self.cellData["spaceID"]:
				self.createCellEntity()

	def onSpaceLoaderDestroyed( self ):
		"""
		The SpaceLoader that created us has been destroyed, which means
		our source geometry is being unloaded.
		"""
		self.respawnInterval = 0
		if self.hasCell:
			self.destroyCellEntity()
		else:
			self.destroy()

	def onLoseCell( self ):
		rsm = None
		if hasattr( self, 'respawnInterval' ) and self.respawnInterval != 0:
			gb = BigWorld.globalBases
			if not gb.has_key( 'RespawnManager' ):
				rsm = BigWorld.createEntity( 'RespawnManager' )
			else:
				rsm = gb['RespawnManager']
			rsm.registerForRespawn( self.__module__, self.entityData, self.respawnInterval )
		self.destroy()

# At the bottom to avoid circular import issue
import Watchers

# FantasyDemo.py
