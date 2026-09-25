#
# Stress test script for World Editor. NOTE currently you must configure
# the location of svn via the SUBVERSION global variable.
#
# USAGE: 
# >>> import SoakTest
# >>> SoakTest.start()
#
# 1. Reverts the current space to clean SVN
# 2. Reloads all chunks
# 3. Performs 10,000 random operations (configurable):
#	    create model, create shell, delete model, delete shell
#    Repeats this 10 times, and then randomly teleports.
# 4. Does a process all at the 50% mark
# 5. Does a process all after finishing all 10,000 operations
# 6. Roams through the space and tries to delete as many items
#    as possible.
# 7. Does another process all.
# 8. Start again from step 1.
#
###############################################################################
import subprocess
import random
import time
import os
import re

import BigWorld
import ResMgr
import WorldEditor
import Math

# TODO: Would be nice to not have this so hard coded.
SUBVERSION = r"C:\Program Files (x86)\CollabNet\Subversion Client\svn.exe"

SHELLS = [ 
	"sets/temperate/shells/beast_room/beast_room.model",
	"sets/temperate/shells/dungeon/exit_shell.model",
	"sets/minspec/shells/house/house_interior.model",
]

PREFABS = [
	"demo_helpers/prefabs/house_well01.prefab",
	"demo_helpers/prefabs/boats01.prefab",
]

MODELS = [
	"sets/urban/props/ac_box/model/ac_box.model",
	"characters/npc/beast/beast.model",
	"characters/npc/beast/beast.model",
	"characters/npc/beast/beast.model",
	"characters/npc/beast/beast.model",
	"characters/npc/beast/beast.model",
	"sets/temperate/props/fd_peasant_hut.model",
	"sets/temperate/props/fd_s_rock_smooth_large.model",
	"sets/temperate/props/fd_rock_sharp_small.model",
	"sets/temperate/props/fd_village_building.model",
	"sets/temperate/props/fd_watch_tower.model",
	"sets/urban/props/garbage_bin/models/garbage_bin_closed_lod01.model",
]

OPERATIONS_PER_TELEPORT = 10
PLACED_THRESHOLD_FOR_DELETE	= 10000
NUMBER_TO_DELETE = 1000
OPERATIONS_BEFORE_PROCESS = 1500

def _placeIndoorChunk( shellModelName, position ):
	chunkSection, chunkName = WorldEditor.createInsideChunkDataSection()
	chunkSection.writeString( "shell/resource", shellModelName )	
	modelSection = ResMgr.openSection( shellModelName )	
	WorldEditor.chunkFromModel( chunkSection, modelSection )
	
	transform = Math.Matrix()
	transform.setTranslate( position )
	
	WorldEditor.createChunk( chunkSection, chunkName, transform )	
	return chunkName

def _getPlacementPoint():
	vDist = 1000.0
	camX, camY, camZ = WorldEditor.camera().position	
	camX = camX + random.uniform( -100, 100 )
	camZ = camZ + random.uniform( -100, 100 )
	colDist = WorldEditor.terrainCollide( (camX, vDist, camZ), (camX, -vDist, camZ) )	
	if colDist < 0:
		return None
	return Math.Vector3( camX, vDist - colDist, camZ )


def _processData():
	oldOpt = WorldEditor.getOptionBool( "fullSave/warnUndoOnProcessData" )
	WorldEditor.setOptionBool( "fullSave/warnUndoOnProcessData", False )
	WorldEditor.save()
	WorldEditor.setOptionBool( "fullSave/warnUndoOnProcessData", oldOpt )

	
def _calculateGridSize():
	mins, maxs = WorldEditor.gridBounds()
	return (( int(mins[0]/100), int(mins[2]/100) ), ( int(maxs[0]/100)-1, int(maxs[2]/100)-1 ))
	
def _calculateGridCenter( grid ):
	return ( grid[0]*100 + 50, grid[1]*100 + 50 )


def _removeAll( path ):
	if 'space.lck' in path:
		return
	if not os.path.isdir(path):
		os.remove(path)
		return
	files=os.listdir(path)
	for x in files:
		fullpath=os.path.join(path, x)
		if os.path.isfile(fullpath):
			os.remove(fullpath)
		elif os.path.isdir(fullpath):
			removeall(fullpath)
	os.rmdir(path)

# http://stackoverflow.com/questions/239340/automatically-remove-subversion-unversioned-files
def _deleteUnversioned( path ):
	unversionedRex = re.compile( '^ ?[\?ID] *[1-9 ]*[a-zA-Z]* +(.*)' )
	cmd = '"%s" status --no-ignore -v %s' % (SUBVERSION, path)
	print "Executing", cmd
	for l in os.popen( cmd ).readlines():
		match = unversionedRex.match( l )
		if match:
			_removeAll( match.group(1) )


class SoakTest:
	
	def __init__( self ):
		self.operations = [
			self._placeRandomShell,
			#self._placeRandomPrefab,
			self._placeRandomModel,
			#self._deleteRandomItem
		]
		
		self.placedShells = []
		self.totalPlacements = 0
		self.totalOperations = 0
		self.shouldStop = False
		self.clearing = False
		self.currentWalkChunk = None

	
	def start( self, skipPreamble=False ):
		self._logEvent( "Starting automatic stress test, space='%s', bounds=%s..." % \
			(WorldEditor.spaceName(), WorldEditor.gridBounds()) )
		if not skipPreamble:
			self.doPreamble()
		else:
			self._logEvent( "Preamble skipped." )
			self.preambleFinished()
		
		
	def stop( self ):
		self.shouldStop = True
		
		
	def preambleFinished( self ):
		self.doStressTesting()

		
	def doPreamble( self ):
	
		self._logEvent( "Reverting to fresh checkout..." )
		self._revertSpace()
	
		self._logEvent( "Running processing tests..." )
		# Reload everything to start afresh, check we are at a clean state.
		WorldEditor.reloadAllChunks( False )
		self._logEvent( "Waiting for chunks to reload..." )
		BigWorld.callback( 10, self._preamblePart2 )
		
		
	def _preamblePart2( self ):
		# This was waiting for chunks to reload
		for key, value in WorldEditor.chunkDirtyCounts().iteritems():
			self.check( value == 0, "%s dirty list should be clean at the start! Maybe SVN revert the test space." % key )
		
		# Dirty everything
		WorldEditor.touchAllChunks()
		for key, value in WorldEditor.chunkDirtyCounts().iteritems():
			self.check( value == 0, "%s should be dirty after touchAllChunks!" % key )
		
		WorldEditor.regenerateLODs()
		self.check( WorldEditor.chunkDirtyCounts()["TerrainLod"] == 0, "regenerateLODs didn't clean all lods!" )
		
		WorldEditor.regenerateThumbnails()
		self.check( WorldEditor.chunkDirtyCounts()["TerrainLod"] == 0, "regenerateThumbnails didn't clean all thumbnails!" )
		
		# Process all data
		_processData()
		for key, value in WorldEditor.chunkDirtyCounts().iteritems():
			self.check( value == 0, "%s should be clean after processData!" % key )
			
		self.preambleFinished()
		
		
	def doStressTesting( self ):
		self._logEvent( "Beginning stress test..." )
		random.seed( 0 )
		self.totalPlacements = 0
		self.operationsSinceTeleport = 0
		self.totalOperations = 0
		self._nextOperation()

	
	def check( self, value, failureMsg ):
		if not bool(value):
			self._logEvent( "ERROR: " + failureMsg )
			
			
	def _nextOperation( self ):
		if self.shouldStop:
			self._logEvent( "Testing has been stopped." )
			self.shouldStop = False
			return
			
		# We need at least the camera chunk available before continuing.
		if WorldEditor.cameraChunkIdentifier() == "":
			BigWorld.callback( 0.1, self._nextOperation )
			return
			
		# Are we in a clearing phase
		if self.clearing:
			if self.totalPlacements > PLACED_THRESHOLD_FOR_DELETE - NUMBER_TO_DELETE:
				# Delete in the camera chunk until we can no longer
				random.choice( [self._deleteRandomItem, self._deleteRandomShell] )()
				delay = self._teleportNextWalkChunk()
				BigWorld.callback( delay, self._nextOperation )
			else:
				self._logEvent( "Finished clearing..." )
				self.clearing = False
				
				self._logEvent( "Processing data..." )
				_processData()
				WorldEditor.clearUndoRedo()
				
				self._logEvent( "Reverting space to fresh checkout..." )
				self._revertSpace()
				self.totalOperations = 0
				
				self._logEvent( "Reloading all chunks..." )
				WorldEditor.reloadAllChunks( False )
				BigWorld.callback( 10.0, self._nextOperation )
		elif self.totalPlacements >= PLACED_THRESHOLD_FOR_DELETE:
			# Start clearing stuff out if we haven't already		
			WorldEditor.clearUndoRedo()
			self._logEvent( "Clearing undo/redo history." )
			self._logEvent( "Hit max number of placed objects, time to clear stuff out..." )
			self.clearing = True
			self.currentWalkChunk = None
			BigWorld.callback( 0, self._nextOperation )
		else:
			if self.operationsSinceTeleport == OPERATIONS_PER_TELEPORT:
				self._randomTeleport()
				self.operationsSinceTeleport = 0
			else:
				self.operationsSinceTeleport += 1
			
			# Normal testing
			nextDelay = random.choice( self.operations )()
			self.totalOperations += 1
			
			if self.totalOperations > OPERATIONS_BEFORE_PROCESS:
				self._midtestProcess()
				self.totalOperations = 0
			else:
				BigWorld.callback( nextDelay, self._nextOperation )
				
	def _revertSpace( self ):
		fullPath = ResMgr.resolveToAbsolutePath( WorldEditor.spaceName() )
		fullPath = fullPath.replace( "/", "\\" )
		
		_deleteUnversioned( fullPath )
		cmd = '"%s" revert -R %s' % (SUBVERSION, os.path.join( fullPath, "*" ))
		print "Executing", cmd
		subprocess.call( cmd )
		
		self.totalPlacements = 0

		
				
	def _midtestProcess( self ):		
		self._logEvent( "_midtestProcess BEFORE process data: memory load = %s, dirty status = %s" % \
			(WorldEditor.memoryLoad(), WorldEditor.chunkDirtyCounts()) )
			
		_processData()
		
		self._logEvent( "_midtestProcess AFTER process data: memory load = %s, dirty status = %s" % \
			(WorldEditor.memoryLoad(), WorldEditor.chunkDirtyCounts()) )
		
		WorldEditor.clearUndoRedo()
		self._logEvent( "Clearing undo/redo history." )
		BigWorld.callback( 1.0, self._nextOperation )
	
	
	def _teleportNextWalkChunk( self ):
		gridMin, gridMax = _calculateGridSize()
		if self.currentWalkChunk is not None:
			nextGridX = self.currentWalkChunk[0] + 1
			nextGridZ = self.currentWalkChunk[1]
			if nextGridX > gridMax[0]:
				nextGridX = gridMin[0]
				nextGridZ += 1
			if nextGridZ > gridMax[1]:
				nextGridX = gridMin[0] # reached the end, wrap back to start
				nextGridZ = gridMin[1]
				
			self.currentWalkChunk = (nextGridX, nextGridZ)
		else:
			self.currentWalkChunk = gridMin
			
		camPos = _calculateGridCenter( self.currentWalkChunk )
		camPos = Math.Vector3( camPos[0], 100, camPos[1] )
		WorldEditor.camera().position = camPos
		return 0.1		
	
	def _randomTeleport( self ):
		bounds = WorldEditor.gridBounds()
		pnt = Math.Vector3()
		pnt.x = random.uniform( bounds[0].x+50, bounds[1].x-50 )
		pnt.y = 200
		pnt.z = random.uniform( bounds[0].z+50, bounds[1].z-50 )
		
		self._logEvent( "_randomTeleport: teleported to " + str(pnt) )
		WorldEditor.camera().position = pnt
		return 0.1
		
		
	def _placeRandomShell( self ):
		pos = _getPlacementPoint()
		if pos is None:
			return 0
		model = random.choice( SHELLS )
		try:
			chunkName = _placeIndoorChunk( model, pos )
			self.totalPlacements += 1
			self.placedShells.append( chunkName )
			self._logEvent( "_placeRandomShell: placed " + model + " at " + str(pos) + " with id " + chunkName )
		except ValueError:
			self._logEvent( "Failed to place shell " + model + " at " + str(pos) + " - probably too close to space boundary." )
		
		return 0.1


	def _deleteRandomShell( self ):
		if len(self.placedShells) == 0:
			return 0
			
		choice = random.choice( self.placedShells )
		
		try:
			WorldEditor.deleteChunk( choice )
			self.placedShells.remove( choice )
			self.totalPlacements -= 1
			self._logEvent( "_deleteRandomShell: Deleted chunk id " + choice )
		except ValueError, e:
			self._logEvent( "_deleteRandomShell: There was a problem trying to delete chunk id '%s'." % e )
		
		return 0.1
		
		
	def _deleteRandomItem( self ):
		chunkID = WorldEditor.outsideChunkIdentifier( WorldEditor.camera().position, True )
		if chunkID == "":
			self._logEvent( "_deleteRandomItem: failed to get chunk ID from camera position." )
			return 0
			
		try:
			chunkItems = WorldEditor.chunkItems( chunkID ).filterTypes( ["ChunkModel"] )
			if len(chunkItems) == 0:
				return 0
		except ValueError:
			self._logEvent( "_deleteRandomItem: chunk %s is not loaded yet." % chunkID )
			return 0
			
		preDeleteCount = len(chunkItems)
		itemToDelete = chunkItems[0]
		assert( len(itemToDelete) == 1 )
		
		WorldEditor.deleteChunkItems( itemToDelete )
		self.totalPlacements -= 1
		
		chunkItems = WorldEditor.chunkItems( chunkID ).filterTypes( ["ChunkModel"] )
		assert( len(chunkItems) == preDeleteCount-1 )

		self._logEvent( "_deleteRandomItem: successfully deleted an item." )
		return 0.1
		
		
	def _placeRandomModel( self ):
		pos = _getPlacementPoint()
		if pos is None:
			return 0
			
		modelName = random.choice( MODELS )
		d = ResMgr.DataSection( "model" )
		d.writeString( "resource", modelName )
		try:
			transform = Math.Matrix()
			transform.setTranslate( pos )
			group = WorldEditor.createChunkItem( d, transform )
			self.totalPlacements += 1
			self._logEvent( "_placeRandomModel: placed " + modelName + " at " + str(pos) )
		except ValueError:
			self._logEvent( "Failed to place model " + modelName + " at " + 
				str(pos) + " - probably too close to space boundary." )
			
		return 0.1
	
		
	def _placeRandomPrefab( self ):
		pos = _getPlacementPoint()
		if pos is None:
			return 0
			
		prefab = random.choice( PREFABS )
		try:
			transform = Math.Matrix()
			transform.setTranslate( pos )
			group = WorldEditor.loadChunkPrefab( prefab, transform )
			self.totalPlacements += 1
			self._logEvent( "_placeRandomPrefab: placed " + prefab + " at " + str(pos) )
		except ValueError:
			self._logEvent( "Failed to place prefab " + prefab + " at " + 
				str(pos) + " - probably too close to space boundary." )
		return 0.1

		
	def _logEvent( self, msg ):
		print time.ctime( time.time() ), msg, "(placements = %d)" % self.totalPlacements



def start():
	t = SoakTest()
	t.start()
