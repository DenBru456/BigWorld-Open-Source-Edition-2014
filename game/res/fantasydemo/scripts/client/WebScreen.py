###This module implements the WebScreen client-only entity type.
###This entity shows WebScreen text when approached.

import math
import BigWorld
import FantasyDemo
import Math
import GUI
import FDGUI
from FDGUI import Minimap
from Helpers import Caps
from Helpers import collide
import VideoScreen
from GameData import WebScreenData
import Keys
import Avatar

class WebScreen( BigWorld.Entity ):
	stdModel = "sets/urban/props/tv/models/tv.model"


	# --------------------------------------------------------------------------
	# Method: __init__
	# Description:
	#	- sets all the basic instance variables which do not change for this  
	#         class
	# --------------------------------------------------------------------------
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.chunkModel = None
		self.targetCaps = [ Caps.CAP_CAN_USE ]
		self.targetFullBounds = True
		self.seen = True
		self.active = False
		self.timerHandle = None
		self.changeYawWhenUsed = False
		self.grabFocus = False
		if self.interactive:
			self.grabFocus = True
		self.feedSources = self.feedSourcesInput.split(';')
		#flag to tell us if the browser is focused
		self.mozillaBrowserFocused = True

	# entity callbacks
	def prerequisites( self ):
		return [ WebScreenData.modelNames[self.webScreenType] ]

	def onEnterWorld( self, prereqs ):
		self.setModel(prereqs)	
		self.model.channels = self.usedTint
		self.model.visible = True
		self.model.scale = self.scale
		#being stored here to make sure this is always available 
		#this information is sometimes not availalbe when this is called form python
		self.nodeTopLeft = self.model.node("HP_top_left")
		self.nodeTopRight = self.model.node("HP_top_right")
		self.nodeBottomLeft = self.model.node("HP_bottom_left")
		Minimap.addEntity( self )
		self.feedIndex = -1
		self.potID = BigWorld.addPot(	Math.Matrix(self.model.matrix),
						self.triggerRadius,
						self.hitPot )
			
		self.webPage = None
		self.active = False
		if self.feedUpdateDelay != 0:
			self._setupTimer()

		if hasattr( BigWorld, "AwesomiumProvider" ):
			self.webPage = BigWorld.AwesomiumProvider( self.width, self.height )
			self.webPage.script = self

	# --------------------------------------------------------------------------
	# Method: setModel
	# Description:
	#	- sets the WebScreen model
	# --------------------------------------------------------------------------
	def setModel( self, prereqs ):
		#for debug prints
		methodName = "WebScreenData.setWebScreenType: "

		#
		# Force to a legal value.
		#
		if not self.webScreenType in WebScreenData.modelNames.keys():
			print methodName + "webScreenType set to illegal value."
			self.webScreenType = WebScreenData.OUTSIDE
		#choose the model
		self.model = prereqs[WebScreenData.modelNames[ self.webScreenType ]]
		#destroy the automatically-created action matcher
		#note that this short-lived action matcher is the only
		#thing currently setting the initial transform of our model.
		self.model.motors = []


	def onLeaveWorld( self ):
		if hasattr( self, "potID" ):
			BigWorld.delPot( self.potID )
			del self.potID
		self.hpTopLeftMatrix = None
		self.hpTopRightMatrix = None
		self.hpBottolLeftMatrix = None
		BigWorld.delTextureFeed(self.textureFeedName)
		self._cancelTimer()
		self.model = None
		self.nodeTopLeft = None
		self.nodeTopRight = None
		self.nodeBottomLeft = None
		if self.webPage is not None:
			self.webPage.script = None
			self.webPage = None
		Minimap.delEntity( self )

	
	# --------------------------------------------------------------------------
	# Method: changeFeed
	# Description:
	#	- sets the current feed (called by onEnterWorld and from the timer
	#         method to set a different webpage/feed
	# --------------------------------------------------------------------------
	def changeFeed( self ):
		if self.webPage is None:
			return
		wasActive = self.active
		if wasActive:
			self._deactivate()
			
		self.feedIndex += 1
		if self.feedIndex >= len(self.feedSources):
			self.feedIndex = 0
			
		feed = self.feedSources[self.feedIndex]
		if self.webPage.url != feed:
			self.webPage.loadURL( feed )
			
		if wasActive:
			self._activate()


	# timer callback
	def _changeFeedFromTimer( self ):
		self.changeFeed()
		self._setupTimer()


	def _setupTimer( self ):
		self.timerHandle = BigWorld.callback( self.feedUpdateDelay, self._changeFeedFromTimer )


	def _cancelTimer( self ):
		if self.timerHandle is not None:
			BigWorld.cancelCallback( self.timerHandle )
		self.timerHandle = None


	def _activate( self ):
		self.active = True
		BigWorld.addTextureFeed( self.textureFeedName, self.webPage)
		

	def _deactivate( self ):
		self.active = False
		BigWorld.delTextureFeed( self.textureFeedName )
		

	# --------------------------------------------------------------------------
	# Method: hitPot
	# Description:
	#	- Called when the player enters / leaves the player only trap.
	# --------------------------------------------------------------------------
	def hitPot( self, enter, id = None ):		
		player = BigWorld.player()
		if not player or not self.webPage: return
		if enter:
			self.changeFeed()
			self._activate()
		else:
			self._deactivate()
			self.webPage.loadURL( "about:blank" )


	def name( self ):
		return "WebScreen"


	#find intersection based on the mouseX and mouseY with the plane of this WebScreen
	def intersectMouseCoordinates( self , mouseX, mouseY ):
		#intersect the ray based on the mouse coordinates with the model plane
		#assuming the model is flat and has 3 hard points showing its limits.
		m =  Math.Matrix(self.nodeTopLeft)
		topLeft = m.applyToOrigin()
		m =  Math.Matrix(self.nodeTopRight)
		topRight = m.applyToOrigin()
		m =  Math.Matrix(self.nodeBottomLeft)
		bottomLeft = m.applyToOrigin()
		#sometimes happens during the first click
		if topLeft[0] - topRight[0] == 0:
			return -1,-1
		#matrix to convert between spaces
		matrixObjSpace = Math.Matrix(self.model.matrix)
		matrixObjSpace.invert()
		# get points in the object coordinates
		posTopLeftObjSpace = matrixObjSpace.applyPoint(topLeft)
		posTopRightObjSpace = matrixObjSpace.applyPoint(topRight)
		posBottomLeftObjSpace = matrixObjSpace.applyPoint(bottomLeft)
		# get the world ray (src and dest)
		src, dst = collide.getMouseTargettingRay()
		#get the ray in object coordinates
		srcObjCoordinates = matrixObjSpace.applyPoint(src)
		dstObjCoordinates = matrixObjSpace.applyPoint(dst)
		dstObjCoordinates -= srcObjCoordinates
		modelPlane = Math.Plane()
		# For debugging of intersection 
		# print "posTopLeft %s posTopRight %s posBottomLeft %s" % (topLeft, topRight, bottomLeft)
		modelPlane.init(posTopLeftObjSpace, posTopRightObjSpace, posBottomLeftObjSpace)
		intersectObjSpace = modelPlane.intersectRay(srcObjCoordinates, dstObjCoordinates)	
		#using the dot product we will find the element factor computed on each of the vectors (posTopRightObjSpace - posTopLeftObjSpace) and (posBottomLeftObjSpace - posTopLeftObjSpace) and we will get the relative length on each dimension (x and y)
		xAxis = posTopRightObjSpace - posTopLeftObjSpace
		xAxisNor = Math.Vector3(xAxis)
		if xAxisNor.lengthSquared < 0.01:
			return -1, -1
		xAxisNor.normalise()
		intersectionVector = intersectObjSpace - posTopLeftObjSpace 
		intersectObjSpaceNor = Math.Vector3(intersectionVector)
		intersectObjSpaceNor.normalise()
		dotX = xAxisNor.dot(intersectObjSpaceNor)
		# For debugging of intersection 
		# print "posTopLeftObjSpace %s posTopRightObjSpace %s posBottomLeftObjSpace %s intersectObjSpace %s intersectObjSpaceNor %s" % (posTopLeftObjSpace, posTopRightObjSpace, posBottomLeftObjSpace, intersectObjSpace, intersectObjSpaceNor) 
		intersectionVectorOnX = dotX * (intersectionVector)
		deltaX = intersectionVectorOnX.length / ((posTopRightObjSpace - posTopLeftObjSpace).length)
		yAxis = posBottomLeftObjSpace - posTopLeftObjSpace
		yAxisNor = Math.Vector3(yAxis)
		if yAxisNor.lengthSquared < 0.01:
			return -1, -1
		yAxisNor.normalise()
		dotY = yAxisNor.dot(intersectObjSpaceNor)
		#out of scope
		if dotY < 0 or dotX < 0:
			return -1, -1
		intersectionVectorOnY = dotY * (intersectionVector)
		deltaY = intersectionVectorOnY.length / ((posBottomLeftObjSpace - posTopLeftObjSpace).length)
		#check for invalid location 
		if deltaX < 0 or deltaX > 1 or deltaY < 0 or deltaY > 1:
			return -1, -1
		return deltaX * self.width, deltaY * self.height


	# --------------------------------------------------------------------------
	# Method: use
	# Description:
	#	- called to use this WebScreen
	# --------------------------------------------------------------------------
	def use( self ):
		
		# If Awesomium is not enabled, do nothing
		if self.webPage is None:
			return

		# Select the WebScreen and inform the Avatar about it.
		if self.interactive:
			player = BigWorld.player()
			if player.currentWebScreen != self:
				if player.currentWebScreen != None:
					player.removeWebScreenFocus()
				self.setFocus(True)
				player.setWebScreenFocus(self)
			else:
				self.setKeyFocus(True)
			#create a click event to make sure the web page also gets focus
			self.handleLMBEventInternal( True )
			self.handleLMBEventInternal( False )

	def handleLMBEventInternal( self, isDown ):
		mp = GUI.mcursor().position
		locationX, locationY  = self.intersectMouseCoordinates( mp.x, mp.y )
		# For debugging of intersection 
		# print "locationX %s locationY %s " % (locationX, locationY)
		if locationX == -1 and locationY == -1:
			return False
		# send the clicks to the screen (adjusted based on the difference between 
		# This WebScreen size and the webpage size
		locationX = locationX * self.webPage.width / self.width
		locationY = locationY * self.webPage.height / self.height
		#print "calling handleMouseButtonEvent %s %s " % (locationX, locationY)
		#make sure the window is focused
		event = BigWorld.KeyEvent( Keys.KEY_LEFTMOUSE, 
			0 if isDown else -1, 0,
			None, (locationX, locationY) )
		self.webPage.injectKeyEvent( event )
		#self.webPage.handleMouseButtonEvent((locationX, locationY), isDown)
		#important to have setKeyFocus here as it makes sure mozilla flash keys
		#work better (not sure why).
		self.setKeyFocus(True)


	def handleKeyEvent( self, event ):
		if event.key == Keys.KEY_ESCAPE:
			BigWorld.player().removeWebScreenFocus()
			return True

		if event.key == Keys.KEY_LEFTMOUSE:
			#Send the mouse event to the WebScreen 
			if self.interactive:
				return self.handleLMBEventInternal(event.isKeyDown())
				return True
		else:
			self.webPage.injectKeyEvent( event )
		
		if event.isMouseButton():
			return False
		#even if the key was not consumed we still don't want it sent to other components
		return True
		return
		character = event.character
		if ( event.isKeyDown() ):
			callKeyboardEvent=False
			callUnicodeEvent=False
			if ( event.key == Keys.KEY_ESCAPE ) :
				usedKey = LLMozlibKeys.LL_DOM_VK_ESCAPE
				callKeyboardEvent=True
			elif ( event.key == Keys.KEY_BACKSPACE ):
				usedKey = LLMozlibKeys.LL_DOM_VK_BACK_SPACE
				callKeyboardEvent=True
			elif ( event.key == Keys.KEY_RETURN ):
				usedKey = LLMozlibKeys.LL_DOM_VK_RETURN
				callKeyboardEvent=True
			elif ( event.key == Keys.KEY_TAB ) :
				usedKey = LLMozlibKeys.LL_DOM_VK_TAB
				callKeyboardEvent=True
			elif ( character is not None ):
				callUnicodeEvent=True
			
			#Now send the key to the correct function.
			if not self.mozillaHandlesKeyboard:
				if callUnicodeEvent:
					self.webPage.handleUnicodeInput(character)
					return 1
				elif callKeyboardEvent:
					self.webPage.handleKeyboardEvent(usedKey)
					return 1
			else:
				return True
		if event.isMouseButton():
			return False
		#even if the key was not consumed we still don't want it sent to other components
		return True


	# --------------------------------------------------------------------------
	# Method: handleMouseMove
	# Description:
	#	- called to handle mouse move events.
	# --------------------------------------------------------------------------
	def handleMouseMove( self, event ):
		if self.interactive:
			#we do the dz (wheel scroll in any case if required)
			if event.dz != 0:
				self.webPage.injectMouseWheelEvent( event.dz )
			mp = GUI.mcursor().position
			locationX, locationY  = self.intersectMouseCoordinates(mp.x, 
										mp.y )
			#invalid location
			if locationX == -1 and locationY == -1:
				return False
			# send the clicks to the screen (adjusted based on the difference between 
			# This WebScreen size and the webpage size
			locationX = locationX * self.webPage.width / self.width
			locationY = locationY * self.webPage.height / self.height
			#self.webPage.handleMouseMove((locationX, locationY))
			self.webPage.injectMouseMoveEvent( locationX, locationY )
			return True
		return False
	
	
	def setKeyFocus( self, value ):
		if self.mozillaHandlesKeyboard:
			if value:
				self.webPage.focus()
			else:
				self.webPage.unfocus()
			self.mozillaBrowserFocused = value
	
	
	def setFocus( self, value ):
		self.setKeyFocus( value )	
	
	def isGame( self ):
		return self.webScreenType == WebScreenData.ARCADE
	
	
	def setDefault(self):
		self.changeFeed()
	
	
	def navigateBack( self ):
		self.webPage.goBack()
	
	
	def navigateForward( self ):
		self.webPage.goForward()
	
	
	def navigate( self, address ):
		self.webPage.loadURL( address )
	
	
	def __str__ (self):
		return "WebScreen %s %s " % (self.position, self.feedSources)
	
	
	def url(self):
		return self.webPage.url
	
	
	def onChangeAddressBar( self, url ):
		usedURL = url
		player = BigWorld.player()
		if isinstance(player, Avatar.Avatar):
			if player.currentWebScreen == self:
				FantasyDemo.rds.fdgui.webControls.editField.script.setText( usedURL )
		return True

#WebScreen.py
