"""This module implements the VideoScreen entity type."""


import BigWorld
import Math
import math
import random
from FDGUI import Minimap
from Helpers import Caps
import FantasyDemo

# ------------------------------------------------------------------------------
# Class VideoScreen:
#
# VideoScreen is an entity that displays the image from a textureFeed.
#
# The bone tv is used as the model, the texture is displayed on there.
# ------------------------------------------------------------------------------
class VideoScreen( BigWorld.Entity ):

	stdModel = "helpers/props/standin.model"
	# the feedsources in a tuple, None means use the video feed camera, an url means navigate to that url
	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- Defines all variables used by the effect entity. This includes
	#	  setting variables to None.
	#	- Does not call any of the accessor methods. Any variables set are
	#	  for the purposes of stability.
	#	- Checks built-in properties set by the client.
	#	- Builds the list binding actionIDs to actions.
	# --------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity.__init__( self )

		#
		# Set all standard entity variables.
		#
		self.targetCaps = [ Caps.CAP_NEVER ]
		self.filter = BigWorld.DumbFilter()
		self.model = None
		self.camera = None
		self.initCallback = 0
		self.timerHandle = None
		self.active = False

	'''This is called by BigWorld when the Entity
		is about to enter the world.  We return a list of
		our prerequisite resources; these will get loaded by
		BigWorld in the background thread for us, before
		EnterWorld is called.
		'''
	def prerequisites( self ):
		return [VideoScreen.stdModel]		


	# --------------------------------------------------------------------------
	# Method: onEnterWorld
	# Description:
	#	- Sets a time for the effect in appear after the model anchor has been
	#	  drawn.
	# --------------------------------------------------------------------------
	def onEnterWorld( self, prereqs ):
		self.model = prereqs[VideoScreen.stdModel]
		self.model.visible = False
		self.focalMatrix = self.model.matrix	
		Minimap.addEntity( self )
		self.init()		


	# --------------------------------------------------------------------------
	# Method: onLeaveWorld
	# Description:
	#	- Destroys the particle system for the effect.
	# --------------------------------------------------------------------------
	def onLeaveWorld( self ):
		self._cancelTimer()
		Minimap.delEntity( self )
		if hasattr( self, "potID" ):
			self.hitPot( 0 )
			BigWorld.delPot( self.potID )
			del self.potID
		BigWorld.delTextureFeed(self.textureFeedName)
		self.sceneRenderer = None
		self.model = None
		self.webPage = None
		self.active = False
		if self.initCallback:
			BigWorld.cancelCallback( self.initCallback )


	def init( self ):
		self.feedSources = self.feedSourcesInput.split(';')
		try:
			self.initCallback = 0

			self.camera = BigWorld.FreeCamera()
			self.camera.fixed = True
			m = Math.Matrix()
			m.setRotateYPR( (self.cameraNode.yaw, self.cameraNode.pitch, self.cameraNode.roll) )
			m.translation = self.cameraNode.position

			m.invert()

			self.camera.set(m)

			self.createSceneRenderer()

			self.potID = BigWorld.addPot(	self.model.matrix,
							self.triggerRadius,
							self.hitPot )
			
			self.webPage = None
			self.useWebPage = False
			self.active = False
			self.feedIndex = -1
			self.changeFeed()
			if self.feedUpdateDelay != 0:
				self._setupTimer()
		except BigWorld.UnresolvedUDORefException:
			self.initCallback = BigWorld.callback(	random.uniform( 9, 11 ), self.init )
		except AttributeError:
			if self.cameraNode == None:
				print "Video screen %d is not linked to a camera node." % (self.id,)


	def changeFeed( self ):
		wasActive = self.active
		if wasActive:
			self.deactivate()
			
		self.feedIndex += 1
		if self.feedIndex >= len(self.feedSources):
			self.feedIndex = 0
			
		feed = self.feedSources[self.feedIndex]
		if feed != "TV":
			if self.webPage == None:
				self.webPage = BigWorld.WebPageProvider(800,600,True,True,u"", "EFFECT_QUALITY")
				if hasattr(self, "ratePerSecond"):
					self.webPage.ratePerSecond = self.ratePerSecond
				else:
					self.webPage.ratePerSecond = 1
			self.useWebPage = True
			if self.webPage.url != feed:
				self.webPage.navigate( feed )
		else:
			self.useWebPage = False
			self.webPage == None 
			
		if wasActive:
			self.activate()

	def _changeFeedFromTimer( self ):
		self.changeFeed()
		self._setupTimer()

	def _setupTimer( self ):
		self.timerHandle = BigWorld.callback( self.feedUpdateDelay, self._changeFeedFromTimer )

	def _cancelTimer( self ):
		if self.timerHandle is not None:
			BigWorld.cancelCallback( self.timerHandle )
		self.timerHandle = None

	def activate( self ):
		self.active = True
		if self.useWebPage == True:
			BigWorld.addTextureFeed( self.textureFeedName, self.webPage.texture )
		else:
			BigWorld.addTextureFeed( self.textureFeedName, self.sceneRenderer.texture )
			self.sceneRenderer.dynamic = 1
		
	def deactivate( self ):
		self.active = False
		if self.useWebPage == False:
			self.sceneRenderer.dynamic = 0
		BigWorld.delTextureFeed( self.textureFeedName )
		

	# --------------------------------------------------------------------------
	# Method: hitPot
	# Description:
	#	- Called when the player enters / leaves the player only trap.
	# --------------------------------------------------------------------------
	def hitPot( self, enter, id = None ):		
		player = BigWorld.player()
		if not player: return
		if enter:
			self.activate()
		else:
			self.deactivate()

	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#		- Uses the Effect. In most cases, effects cannot be selected nor
	#		  used, but it helps debugging to allow the code to be changed to
	#		  allow it.
	# --------------------------------------------------------------------------
	def use( self ):
		pass


	# -------------------------------------------------------------------------
	# this method sets up the py scene renderer.
	# -------------------------------------------------------------------------
	def createSceneRenderer( self ):		
		self.sceneRenderer = BigWorld.PySceneRenderer( 512, 512 )
		self.sceneRenderer.skipFrames = self.skipFrames
		self.sceneRenderer.staggered = True
		self.sceneRenderer.fov = 1.047
		self.sceneRenderer.cameras = (self.camera,)


	# --------------------------------------------------------------------------
	# Method: name
	#
	# This method returns the name of this class.
	# --------------------------------------------------------------------------
	def name( self ):
		return "Video Screen"


#VideoScreen.py
