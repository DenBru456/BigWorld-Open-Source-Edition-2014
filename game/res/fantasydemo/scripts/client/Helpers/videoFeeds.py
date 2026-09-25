import BigWorld
import GUI
import ResMgr
import Keys
import Math
from PyGUI import PyGUIBase

s_videoFeeds = None

def createStriffFeed():
	camera = BigWorld.FreeCamera()
	m = Math.Matrix()
	m.setRotateYPR( (2.69752,0.467126,0.0) )
	m.translation = (-36.5,28.6,87.46)
	s = GUI.load("gui/video_feed.gui")
	camera.set(m)
	s.script.active(1,camera)
	return s

def createExternalFeed( feedName, matrixProvider ):
	sceneRenderer = BigWorld.PySceneRenderer( 64, 64 )
	camera = BigWorld.FreeCamera()
	camera.invViewProvider = matrixProvider
	sceneRenderer.cameras = [camera]
	sceneRenderer.dynamic = 1
	sceneRenderer.render()
	BigWorld.addTextureFeed( feedName, sceneRenderer.texture )
	return sceneRenderer

# -------------------------------------------------------------------------
# this class manages all video feeds.
# -------------------------------------------------------------------------
class VideoFeeds:
	# -------------------------------------------------------------------------
	# this method initialises the video feed helper class.
	# -------------------------------------------------------------------------
	def __init__( self ):
		global s_videoFeeds
		s_videoFeeds = self
		self.active = 0
		self.sceneRenderer = None
		self.feeds = []
		self.cameras = []
		self.staticRange = 80.0
		self.range = 100.0
		self.idx = -1

	# -------------------------------------------------------------------------
	# this method sets up the py scene renderer.
	# -------------------------------------------------------------------------
	def createSceneRenderer( self ):
		self.sceneRenderer = BigWorld.PySceneRenderer( 512, 512 )
		self.sceneRenderer.fov = 1.047
		self.sceneRenderer.cameras = self.cameras
		self.sceneRenderer.render()

	# -------------------------------------------------------------------------
	# this method adds the given video feed.
	# -------------------------------------------------------------------------
	def add( self, videoFeed ):
		if not self.sceneRenderer:
			self.createSceneRenderer()

		if not videoFeed in self.feeds:
			self.feeds.append( videoFeed )
			videoFeed.component.scene.texture = self.sceneRenderer.texture
			self.onAlterFeeds()
			#GUI.addRoot( videoFeed.component )

		if not self.active:
			self.active = 1.0
			BigWorld.callback( 1.0, self.checkFeeds )

	# -------------------------------------------------------------------------
	# this method removes the given video feed.
	# -------------------------------------------------------------------------
	def rem( self, videoFeed ):
		if videoFeed in self.feeds:
			self.feeds.remove( videoFeed )
			self.onAlterFeeds()
			#GUI.delRoot( videoFeed.component )
		if not len(self.feeds):
			self.active = 0.0

	# -------------------------------------------------------------------------
	# this method removes all video feeds.
	# -------------------------------------------------------------------------
	def removeAll( self ):
		for videoFeed in self.feeds:
			self.feeds.remove( videoFeed )
			#GUI.delRoot( videoFeed.component )
		self.onAlterFeeds()

	# -------------------------------------------------------------------------
	# this method shows/hides all video feeds.
	# -------------------------------------------------------------------------
	def visible( self, state ):
		for videoFeed in self.feeds:
			videoFeed.component.visible = state

	# -------------------------------------------------------------------------
	# this method is called when we have gained or lost a video feed.
	# we refresh the scene renderer's list of cameras, and layout ourselves.
	# -------------------------------------------------------------------------
	def onAlterFeeds( self ):
		self.cameras = []
		for feed in self.feeds:
			self.cameras.append( feed.camera )
		self.doLayout()
		self.sceneRenderer.cameras = self.cameras
		if len(self.cameras):
			self.sceneRenderer.dynamic=1
		else:
			self.sceneRenderer.dynamic=0

	# -------------------------------------------------------------------------
	# this method lays out all active video feeds.
	# -------------------------------------------------------------------------
	def doLayout( self ):
		num = len( self.feeds )
		if num == 0:
			return

		example = self.feeds[0]
		w = example.component.width
		h = example.component.height

		dx = w
		du = 1.0 / num
		i = 0
		for feed in self.feeds:
			(discardX,discardY,z) = feed.component.position
			x = (0.85 - w/2.0) - (i%4)*dx
			y = -0.85+h/2+(i/4)*h
			feed.moveTo( (x,y,0.9) )
			x1 = i * du
			x2 = (i+1) * du
			mc = ((x1,0),(x1,1),(x2,1),(x2,0))
			feed.component.scene.mapping = mc
			i+=1

	# -------------------------------------------------------------------------
	# this method selects a particular video feed.
	# -------------------------------------------------------------------------
	def select( self, idx ):
		oldIdx = self.idx

		if idx < 0:
			idx = 0

		if idx >= len( self.feeds ):
			idx = len( self.feeds ) - 1

		if not idx == oldIdx:

			if oldIdx != -1:
				oldFeed = self.feeds[oldIdx]
				oldFeed.component.select.colour=(0,0,0,255)
				try:
					oldFeed.camera.fixed = 1
				except:
					try:
						oldFeed.camera.source = None
					except:
						pass

			if idx != -1:
				newFeed = self.feeds[idx]
				newFeed.component.select.colour=(128,255,128,255)
				try:
					newFeed.camera.fixed = 0
				except:
					try:
						newFeed.camera.source = BigWorld.dcursor().matrix
					except:
						pass
			self.idx = idx
		return self.idx

	# -------------------------------------------------------------------------
	# this method deselects all video feeds.
	# -------------------------------------------------------------------------
	def deselectAll( self ):
		for feed in self.feeds:
			try:
				feed.camera.fixed=1
			except:
				try:
					feed.camera.source = None
				except:
					pass
			feed.component.select.colour=(0,0,0,255)
			self.idx = -1

	# -------------------------------------------------------------------------
	# callback : this method checks all video feed for validity.
	# -------------------------------------------------------------------------
	def checkFeeds( self ):
		#is length has gone to 0, stop the callbacks
		if not self.active:
			return

		player = BigWorld.player()
		for feed in self.feeds:
			camera = feed.camera
			if camera != None:
				pos = camera.position
				distance = pos.distTo( player.position )
				if distance < self.staticRange:
					feed.setStatic( 0.0 )
				else:
					amount = (distance - self.staticRange)/	\
						(self.range - self.staticRange)
					feed.setStatic( amount )
			else:
				feed.setStatic( amount )

		BigWorld.callback( 1.0, self.checkFeeds )


# -------------------------------------------------------------------------
# this class implements a single video feed.
# -------------------------------------------------------------------------
class VideoFeed( PyGUIBase ):

	factoryString="PyGUI.VideoFeed"

	def __init__( self, component ):
		PyGUIBase.__init__( self, component )
		self.isActive = 0
		self.inRange = 1
		self.camera = None
		self.targetID = 0
		self.inTransit = 0
		self.tr = Math.Matrix()
		self.tr.setIdentity()
		self.mx = Math.Matrix()
		self.mx.setIdentity()
		self.target = Math.Matrix()
		self.target.setIdentity()
		self.bug = None
		self.guiViewer = None

	# -------------------------------------------------------------------------
	# this method activates the video feed.
	# -------------------------------------------------------------------------
	def active( self, state, camera = None ):
		if state == self.isActive:
			return
		self.isActive = state

		if self.isActive:
			if camera:
				self.camera = camera
			assert self.camera
			s_videoFeeds.add( self )
		else:
			s_videoFeeds.rem( self )

	# Someone has changed our camera
	def setCamera( self, newCam ):
		self.camera = newCam
		if self.guiViewer:
			self.guiViewer.modCurrentFeedCamera()

	# -------------------------------------------------------------------------
	# These methods are needed by the gui system.
	# -------------------------------------------------------------------------
	def handleAxisEvent( self, event ):
		return 0

	def handleMouseEvent( self, event ):
		return 0

	def handleKeyEvent( self, event ):
		return False

	def focus( self, state ):
		pass

	def onLoad( self, section ):
		pass

	def onSave( self, section ):
		pass

	def onBound( self ):
		PyGUIBase.onBound( self )
		offset = self.component.scene.position
		offset[2] = 0
		self.tr.setTranslate( offset )
		self.component.scene.transform.target = self.target
		self.moveTo( self.component.position )

	def moveTo( self, pos ):
		self.component.position = pos
		self.component.select.position = pos
		self.component.scene.position = (0.0,0.0,pos[2])
		#self.component.scene.static.position = (0.0,0.0,pos[2])
		self.tr.setTranslate( (pos[0],pos[1],0.0) )
		self.compileTransform()
		self.component.scene.transform.reset()

	def compileTransform( self ):
		self.target = self.tr
		self.target.preMultiply( self.mx )
		self.component.scene.transform.target = self.target

	# -------------------------------------------------------------------------
	# This method is called when the video feed target enters our valid range.
	# -------------------------------------------------------------------------
	def onEnterRange( self ):
		if self.inTransit == 0:
			self.inTransit = 1
			self.mx.setScale( (100.0, 1.0, 1.0) )
			self.compileTransform()
			self.component.scene.transform.blend = 1
			self.component.scene.transform.eta = 0.2
			BigWorld.callback( 0.3, self.onEnterRange2 )

	def onEnterRange2( self ):
		if self.inTransit == 1:
			self.inTransit = 2
			self.mx.setScale( (1.0, 100.0, 1.0) )
			self.compileTransform()
			self.component.scene.transform.blend = 1
			self.component.scene.transform.eta = 0.2
			BigWorld.callback( 0.3, self.onEnterRange3 )

	def onEnterRange3( self ):
		if self.inTransit == 2:
			self.mx.setScale( (1.0, 1.0, 1.0) )
			self.compileTransform()
			self.component.scene.transform.blend = 0
			self.inRange = 1
			self.inTransit = 0

	# -------------------------------------------------------------------------
	# This method is called when the video feed target leaves our valid range.
	# -------------------------------------------------------------------------
	def onLeaveRange( self ):
		if self.inTransit == 0:
			self.inTransit = 1
			self.mx.setScale( (1.0, 0.01, 1.0) )
			self.compileTransform()
			self.component.scene.transform.blend = 1
			self.component.scene.transform.eta = 0.2
			BigWorld.callback( 0.3, self.onLeaveRange2 )

	def onLeaveRange2( self ):
		if self.inTransit == 1:
			self.inTransit = 2
			self.mx.setScale( (0.01, 1.0, 1.0) )
			self.compileTransform()
			self.component.scene.transform.blend = 1
			self.component.scene.transform.eta = 0.2
			BigWorld.callback( 0.3, self.onLeaveRange3 )

	def onLeaveRange3( self ):
		if self.inTransit == 2:
			self.mx.setScale( (1.0, 1.0, 1.0) )
			self.compileTransform()
			self.component.scene.transform.blend = 0
			self.mx.setScale( (0.01, 0.01, 0.01) )
			self.inRange = 0
			self.inTransit = 0

	# -------------------------------------------------------------------------
	# Callback: sets the amount of static on the video feed.
	# -------------------------------------------------------------------------
	def setStatic ( self, amount ):		
		return
		if amount > 1.0:
			#self.component.scene.static.shader.value = 1.0
			if self.inRange:
				if not self.inTransit:
					self.onLeaveRange()
		else:
			#self.component.scene.static.shader.value = amount
			if not self.inRange:
				if not self.inTransit:
					self.onEnterRange()



# Initialise the singleton
VideoFeeds()

# videoFeeds.py