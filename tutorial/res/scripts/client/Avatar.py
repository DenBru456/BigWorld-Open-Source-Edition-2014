import BigWorld
import Keys

import chapters
import tutorial

if tutorial.includes( chapters.CHAT_CONSOLE ):
	from Helpers import ChatConsole

class Avatar( BigWorld.Entity ):

	def onEnterWorld( self, prereqs ):
		if tutorial.includes( chapters.CLIENT_SERVER ):		
			# Set the position/movement filter to correspond to an avatar
			self.filter = BigWorld.AvatarFilter()

			# Load up the bipedgirl model
			self.model = BigWorld.Model( "characters/bipedgirl.model" )
		else:
			pass

	if tutorial.includes( chapters.CHAT_CONSOLE ):
		def say( self, msg ):

			ChatConsole.ChatConsole.instance().write(
				"%d says: %s" % (self.id, msg) )


class PlayerAvatar( Avatar ):

	def onEnterWorld( self, prereqs ):

		Avatar.onEnterWorld( self, prereqs )

		# Set the position/movement filter to correspond to an player avatar
		self.filter = BigWorld.PlayerAvatarFilter()

		# Setup the physics for the Avatar
		self.physics = BigWorld.STANDARD_PHYSICS
		self.physics.velocityMouse = "Direction"
		self.physics.collide = True
		self.physics.fall = True


	def handleKeyEvent( self, event ):

		if event.isRepeatedEvent():
			return

		isDown = event.isKeyDown()

		# Get the current velocity
		v = self.physics.velocity

		# Update the velocity depending on the key input
		if event.key == Keys.KEY_W:
			v.z = isDown * 5.0
		elif event.key == Keys.KEY_S:
			v.z = isDown * -5.0
		elif event.key == Keys.KEY_A:
			v.x = isDown * -5.0
		elif event.key == Keys.KEY_D:
			v.x = isDown * 5.0

		# Save back the new velocity
		self.physics.velocity = v

# Avatar.py
