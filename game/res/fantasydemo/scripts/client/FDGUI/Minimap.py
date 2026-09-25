import BigWorld
import GUI
import Helpers.PyGUI.ToolTip as ToolTip
from Helpers.PyGUI.ToolTip import ToolTipInfo
from Helpers.PyGUI.ToolTip import ToolTipManager
import Helpers.PyGUI as PyGUI
import ResMgr
import Math
import FantasyDemo
import BWReplay
import Keys
import Avatar
from Math import Matrix
from functools import partial

smallMinimapName = "gui/minimap_small.gui"
largeMinimapName = "gui/minimap_large.gui"

#for preload reasons only
smallMinimapDS = ResMgr.openSection( smallMinimapName )
largeMinimapDS = ResMgr.openSection( largeMinimapName )

class MinimapWindow( PyGUI.Window ):

	def _setparent( self, parent ):
		PyGUI.Window._setparent( self, parent )
		for child in self.component.children:
			child[1].script.parent = parent
	parent = property(PyGUI.Window._getparent, _setparent)


#------------------------------------------------------------------------------
# This class handles the minimap itself, not the border around it or the
# buttons.
#------------------------------------------------------------------------------
class Minimap( PyGUI.PyGUIBase ):
	BK_LAYER = 0
	OUTDOOR_LAYER = 1
	INDOOR_LAYER = 2

	def __init__( self, component ):
		PyGUI.PyGUIBase.__init__( self, component )
		self.toolTipInfo = ToolTipInfo( self.component, "tooltip1line" )
		self.toolTipInfo.infoDictionary["shortcut"] = ""
		self.toolTipInfo.delayType = ToolTip.IMMEDIATE_TOOL_TIP
		self.toolTipInfo.placement = ToolTip.PLACE_ABOVE
		self.handleMap = {}
		self.maxZoom = 1500
		self.minZoom = 100
		self.zoomFactor = 2.0
		self.component.pointSizeScaling = (12.0, -6.0/5000.0)
		self.component.focus = True
		self.pickedEntry = None

	def onBound( self ):
		PyGUI.PyGUIBase.onBound( self )
		self.smallMinimap = GUI.load(smallMinimapName)
		self.largeMinimap = GUI.load(largeMinimapName)
		self.smallMinimap.script.minimap = self.component
		self.largeMinimap.script.minimap = self.component
		self.maximised = True
		self.maximise( False )


	def _minimap( self ):
		return self.component


	def _setparent( self, parent ):
		PyGUI.PyGUIBase._setparent( self, parent )
		self.largeMinimap.script.parent = parent
		self.smallMinimap.script.parent = parent
	parent = property(PyGUI.PyGUIBase._getparent, _setparent)


	def add( self, entity ):
		try:
			col = entity.minimapColour
		except:
			col = (128,128,128,255)

		entity.minimapHandle = self.component.addSimple(entity.matrix, col)
		self.handleMap[entity.minimapHandle] = entity.id


	def remove( self, entity ):
		if hasattr( entity, "minimapHandle" ):
			self.component.remove(entity.minimapHandle)


	def onEntryBlur( self, handle ):
		self.pickedEntry = None
		pass


	def onEntryFocus( self, handle ):
		self.pickedEntry = handle
		BigWorld.callback( 0.0, partial(self._updateToolTip, handle) )


	def _updateToolTip( self, handle ):
		self.toolTipInfo.infoArea = self._toolTipArea()
		id = self.handleMap[handle]
		try:
			name = FantasyDemo.getEntityName( id, True )
			self.toolTipInfo.infoDictionary["text"] = name
			ToolTipManager.instance.setupToolTip(self.component, self.toolTipInfo)
		except KeyError:
			pass


	def _toolTipArea( self ):
		s = self.component.simpleEntrySize * 1.0
		pos = GUI.mcursor().position
		pos = self.component.screenToLocal(pos)
		toolTipArea = (pos[0]-s, pos[1]-s, pos[0]+s, pos[1]+s)
		return toolTipArea


	def ensureZoomInRange( self ):
		m = self._minimap()
		m.range = max( m.range, self.minZoom )
		m.range = min( m.range, self.maxZoom )


	def zoomIn( self ):
		m = self._minimap()
		range = m.range
		zoomRange = self.maxZoom - self.minZoom
		m.range = m.range / self.zoomFactor
		if m.range < self.minZoom:
			m.range = self.minZoom


	def zoomOut( self ):
		m = self._minimap()
		range = m.range
		zoomRange = self.maxZoom - self.minZoom
		m.range = m.range * self.zoomFactor
		if m.range > self.maxZoom:
			m.range = self.maxZoom


	def maximise( self, state = True ):
		if self.maximised == state:
			return

		from FDGUI import Z_ORDER_SMALLMINIMAP_MAP
		from FDGUI import Z_ORDER_SMALLMINIMAP_FRAME
		from FDGUI import Z_ORDER_LARGEMINIMAP_FRAME
		from FDGUI import Z_ORDER_LARGEMINIMAP_MAP

		self.maximised = state
		container = self.component.parent

		# NOTE : large/small minimap overlays are activated into the same
		# root as the container's root, not this component's root.
		# This is because this minimap requires a dummy parent
		# window for layout purposes only (MinimapWindow script).

		if self.maximised:
			self.smallMinimap.script.active(False)
			self.largeMinimap.script.active(True)
			(x,y,z) = self.component.position
			self.component.position = (x,y,Z_ORDER_LARGEMINIMAP_MAP)
			(x,y,z) = self.largeMinimap.position
			self.largeMinimap.position = (x,y,Z_ORDER_LARGEMINIMAP_FRAME)
			container.position = (0,0,Z_ORDER_LARGEMINIMAP_MAP)
			container.verticalAnchor = "CENTER"
			container.horizontalAnchor = "CENTER"
			container.size = self.largeMinimap.script.containerSize
			container.m.size = self.largeMinimap.script.minimapSize
			self.component.maskName = self.largeMinimap.script.maskName
		else:
			self.largeMinimap.script.active(False)
			self.smallMinimap.script.active(True)
			(x,y,z) = self.component.position
			self.component.position = (x,y,Z_ORDER_SMALLMINIMAP_MAP)
			(x,y,z) = self.smallMinimap.position
			self.smallMinimap.position = (x,y,Z_ORDER_SMALLMINIMAP_FRAME)
			container.position = (1,1,Z_ORDER_SMALLMINIMAP_MAP)
			container.verticalAnchor = "TOP"
			container.horizontalAnchor = "RIGHT"
			container.size = self.smallMinimap.script.containerSize
			container.m.size = self.smallMinimap.script.minimapSize
			self.component.maskName = self.smallMinimap.script.maskName

		if container.parent is not None:
			container.parent.reSort()

		#self.ensureZoomInRange()


	def _normalisedMousePosition( self ):
		c = self.component
		pos = GUI.mcursor().position
		pos = c.screenToLocal( pos )
		pos[0] = pos[0] / c.width
		pos[1] = pos[1] / c.height
		if (pos[0] < 0) or (pos[0] > 1):
			return
		if (pos[1] < 0) or (pos[1] > 1):
			return
		if c.heightMode is not "PIXEL":
			pos[1] = 1.0 - pos[1]
		pos[0] = (pos[0] - 0.5) * 2.0
		pos[1] = (pos[1] - 0.5) * 2.0
		#print "teleportToMousePosition - normalised coordinates", pos[0], pos[1]
		return pos

	def handleTeleport( self ):
		if self.teleportToEntity():
			return True
		else:
			self.teleportToMousePosition()
			return True

	def teleportToMousePosition( self ):
		c = self.component
		pos = self._normalisedMousePosition()
		if pos is None:
			# Mouse was outside the view
			return

		try:
			m = Math.Matrix( c.viewpoint )
		except:
			m = Math.Matrix( BigWorld.camera().invViewMatrix )
		center = m.applyToOrigin()
		#print "teleportToMousePosition - center of map, range", center[0], center[2], c.range
		startPos = Math.Vector3( pos[0] * c.range + center[0], center[1] + 500.0, pos[1] * c.range + center[2] )
		endPos = Math.Vector3( startPos[0], startPos[1] - 1000.0, startPos[2] )
		
		spaceID = -1
		if BWReplay.isLoaded():
			spaceID = BWReplay.spaceID()
		elif BigWorld.player():
			spaceID = BigWorld.player().spaceID
		colres = BigWorld.collide( spaceID, startPos, endPos )

		#print "collision start, end, colres : ", startPos, endPos, colres
		if colres != None:
			(pt, tri, mat) = colres
			if BigWorld.player():
				BigWorld.player().physics.teleport( pt )
			elif BWReplay.isLoaded():
				# Move to 3 meters above pt
				FantasyDemo.freeCamera( True )
				viewMatrix = Matrix()
				viewMatrix.lookAt( pt + (0,3,0),
					BigWorld.camera().direction, (0,1,0))
				BigWorld.camera().set( viewMatrix )
				c.viewpoint = BigWorld.camera().invViewMatrix
		else:
			FantasyDemo.addChatMsg( -1, "Cannot teleport this far away." )
			FantasyDemo.addChatMsg( -1, "Please try somewhere closer," )
			FantasyDemo.addChatMsg( -1, "Or wait for more of the world to load." )

	def teleportToEntity( self ):
		if not BWReplay.isLoaded() or (self.pickedEntry is None):
			return False

		try:
			entityID = self.handleMap[ self.pickedEntry ]
			return BWReplay.getReplayHandler().followEntity( entityID )
		except KeyError:
			pass

		return False

	def handleMouseButtonEvent( self, comp, event ):
		if event.isKeyDown():
			actionName = FantasyDemo.rds.keyBindings.getActionForKeyState( event.key )
			# Only the actions in this list are allowed for clicks on the minimap
			if actionName in ['Teleport']:
				return False

		return True


#utility fn to add/del an entity to/from the minimap
def addEntity( entity ):
	try:
		minimap = FantasyDemo.rds.fdgui.minimap.m.script
	except AttributeError:
		return		
	minimap.add( entity )


def delEntity( entity ):
	try:
		minimap = FantasyDemo.rds.fdgui.minimap.m.script
	except AttributeError:
		return		
	minimap.remove( entity )


class MinimapInfo:
	#This class static serial number helps us ignore late / out of order
	#callbacks, necessary since we do asnychronous loading of files.
	serial = {}
	
	def __init__( self, layerNum = Minimap.OUTDOOR_LAYER ):
		self.textureName = ""
		self.range = 0.0
		self.worldMapWidth = 1000.0
		self.worldMapHeight = 1000.0
		self.worldMapAnchor = (0,0)
		self.layerNum = layerNum
		self.ignoreHandDrawn = False
		self.rotate = False


	#Apply this minimap info to the given minimap. We may require
	#a texture map to load, and we may also need to load a space.settings
	#file to retrieve the space bounds.  These are loaded in the background
	#thread.  The serial number is used to ignore out-of-order callbacks
	#from these asnychronous load methods.
	def apply( self, minimap, serial = -1, verifyFn = None ):
		if serial == -1:
			try:
				MinimapInfo.serial[self.layerNum] += 1
			except KeyError:
				MinimapInfo.serial[self.layerNum] = 0
			serial = MinimapInfo.serial[self.layerNum]
			
		if serial != MinimapInfo.serial[self.layerNum]:
			return

		if self.textureName != None:
			BigWorld.loadResourceListBG( (self.textureName,), partial(self._onLoadTexture,minimap,serial,verifyFn) )
		else:
			spaceID = None
			if BWReplay.isLoaded():
				spaceID = BWReplay.spaceID()
			elif BigWorld.player():
				spaceID = BigWorld.player().spaceID
			try:
				spaceName = FantasyDemo.rds.spaceNameMap[spaceID]
			except:
				spaceName = "spaces/navgen_test_space"
			self.textureName = spaceName + "/space.thumbnail.dds"
			callback = partial(self._onLoadSpaceSettings,minimap,serial,verifyFn)
			settingsFile = spaceName+"/space.settings"
			BigWorld.loadResourceListBG((settingsFile,), callback)


	#Get the minimap information from space.settings.  If the space
	#settings file has no minimap information, then use the default
	#space map from World Editor, and read the bounds in from the
	#space bounds.
	def _onLoadSpaceSettings( self, minimap, serial, verifyFn, resourceRef ):
		if serial != MinimapInfo.serial[self.layerNum]:
			return
					
		ds = resourceRef.values()[0]
		
		bounds = ds["bounds"]
		minX = bounds.readInt("minX",-5)
		maxX = bounds.readInt("maxX",4)
		minY = bounds.readInt("minY",-5)
		maxY = bounds.readInt("maxY",4)
		chunkSize = ds.readFloat( "chunkSize", 100.0 )
		self.worldMapWidth = ((maxX - minX) + 1) * chunkSize
		#NOTE - the automatic outdoor space map we use are upside-down,
		#so we need to negate the y-axis here
		self.worldMapHeight = -((maxY - minY) + 1) * chunkSize
		xCenter = (minX * chunkSize) + self.worldMapWidth / 2.0
		yCenter = (minY * chunkSize) + -self.worldMapHeight / 2.0
		self.worldMapAnchor = (xCenter, yCenter)

		if not self.ignoreHandDrawn and ds.has_key( "minimap" ):
			ds = ds["minimap"]
			self.textureName = ds.readString( "mapName" )
			self.worldMapWidth = ds.readFloat( "worldMapWidth", self.worldMapWidth )
			self.worldMapHeight = ds.readFloat( "worldMapHeight", self.worldMapHeight )
			self.worldMapAnchor = ds.readVector2( "worldMapAnchor" )
			
		self.apply( minimap, serial, verifyFn )


	def _onLoadTexture( self, minimap, serial, verifyFn, resourceRef ):
		if serial != MinimapInfo.serial[self.layerNum]:
			return
			
		if verifyFn != None:
			if not verifyFn():
				return

		minimap.delTextureLayer( self.layerNum )
		minimap.addTextureLayer( self.layerNum, resourceRef[self.textureName], (self.worldMapWidth,self.worldMapHeight), self.worldMapAnchor )		


#utility fn to get the current indoor / outdoor minimaps
def getBkMapInfo():
	mi = MinimapInfo( Minimap.BK_LAYER )
	mi.ignoreHandDrawn = True
	mi.textureName = None
	mi.worldMapWidth = 0.0
	mi.worldMapHeight = 0.0
	mi.worldMapAnchor = (0.0,0.0)
	return mi


def getOutdoorMapInfo():
	mi = MinimapInfo( Minimap.OUTDOOR_LAYER )
	mi.textureName = None
	mi.worldMapWidth = 0.0
	mi.worldMapHeight = 0.0
	mi.worldMapAnchor = (0.0,0.0)
	return mi


def getIndoorMapInfo():
	player = BigWorld.player()
	if player and hasattr( player, "triggeredIndoorMapEntity" ):
		try:
			mapInfoEntity = BigWorld.entities[player.triggeredIndoorMapEntity]
			return mapInfoEntity.mapInfo()
			#print "Got indoor minimap info from entity"
			return
		except KeyError:
			pass

	return getOutdoorMapInfo()


def isIndoors():
	return BigWorld.player() and BigWorld.player().inside


#callback fn.   update the minimap
def onChangeEnvironments( inside ):
	import IndoorMapInfo
	minimap = FantasyDemo.rds.fdgui.minimap.m
	indoorMapInfo = getIndoorMapInfo()
	outdoorMapInfo = getOutdoorMapInfo()

	bkMapInfo = getBkMapInfo()
	if BigWorld.player() != None or BWReplay.isLoaded():
		bkMapInfo.apply( minimap )

		if inside:
			indoorMapInfo.apply( minimap, verifyFn = isIndoors )
		else:
			minimap.delTextureLayer( Minimap.INDOOR_LAYER )
			outdoorMapInfo.apply( minimap )
