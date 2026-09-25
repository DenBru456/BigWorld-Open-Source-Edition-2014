import BigWorld
import GUI
import FMOD

import random

ENABLE_DEBUGGING = False

class SoundEmitter( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )

	def onEnterWorld( self, prereqs ):
		
		if ENABLE_DEBUGGING:
			self.model = BigWorld.Model( "helpers/models/unit_cube.model" )
			self.sound = None

			t = GUI.Text( "Sound: %s" % self.eventName )
			t.explicitSize = True
			t.height = 0.75
			t.width = 0
			t.filterType = "LINEAR"
			t.verticalAnchor = "BOTTOM"
			t.position = (0, self.model.height + 0.1, 0)
			t.colourShader = GUI.ColourShader()
			t.colourShader.start = (255, 64, 0, 255)
			t.colourShader.middle = (255, 128, 64, 255)
			t.colourShader.end = (255, 255, 255, 255)
			t.colourShader.speed = 0.5
			t.colourShader.value = 1.0
			t.colourShader.reset()

			attch = GUI.Attachment()
			attch.faceCamera = True
			attch.component = t
			
			self.model.root.attach( attch )
			self.debugAttachment = attch
		else:
			self.model = BigWorld.Model( "helpers/models/unit_cube.model" )
			self.model.visible = False
			
		if self.initialDelay <= 0.0:
			self.playNext()
		else:
			self._setReplayTimer( self.initialDelay + self.delayVariation * random.random() )
				

	def onLeaveWorld( self ):
		if self.sound is not None:
			self.sound.stop()
			
		self.sound = None
		self.model = None

		
	def playNext( self ):
		if self.isDestroyed:
			return
		if not self.inWorld:
			return
	
		self.sound = None
		self.sound = self.model.playSound( self.eventName )

		if self.replayDelay > 0.0:
			self._setReplayTimer( self.replayDelay + self.delayVariation * random.random() )
			
		if ENABLE_DEBUGGING:
			self.debugAttachment.component.colourShader.value = 0.0
			self.debugAttachment.component.colourShader.reset()
			self.debugAttachment.component.colourShader.value = 1.0

			
	def _setReplayTimer( self, delay ):
		self._cancelReplayTimer()
		self._replayTimer = BigWorld.callback( delay, self.playNext )

		
	def _cancelReplayTimer( self ):
		id = getattr( self, "_replayTimer", None )
		if id is not None:
			BigWorld.cancelCallback( id )
			self._replayTimer = None

