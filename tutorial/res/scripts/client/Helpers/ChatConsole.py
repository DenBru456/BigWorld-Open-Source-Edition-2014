import string
import BigWorld
import GUI
import Keys
import collections

class ChatConsole( object ):

	sInstance = None

	def __init__( self, numVisibleLines = 4 ):

		self.numVisibleLines = numVisibleLines
		self.lines = collections.deque()
		self.editString = ""

		self.box = GUI.Window( "system/maps/col_white.bmp" )
		self.box.position = ( -1, -1, 0 )
		self.box.verticalAnchor = "BOTTOM"
		self.box.horizontalAnchor = "LEFT"
		self.box.colour = ( 0, 0, 0, 128 )
		self.box.materialFX = "BLEND"
		self.box.width = 2
		self.box.script = self

		self.box.text = GUI.Text()
		self.box.text.verticalPositionMode = "CLIP"
		self.box.text.horizontalPositionMode = "CLIP"
		self.box.text.position = ( -1, -1, 0 )
		self.box.text.verticalAnchor = "BOTTOM"
		self.box.text.horizontalAnchor = "LEFT"
		self.box.text.colourFormatting = True
		self.box.text.multiline = True

		GUI.addRoot( self.box )

		self.active = True
		self.update()
		self.box.height = self.box.text.height * ( numVisibleLines + 1 )
		self.editing( False )


	@classmethod
	def instance( cls ):
		"""
		Static access to singleton instance.
		"""

		if not cls.sInstance:
			cls.sInstance = ChatConsole()

		return cls.sInstance


	def editing( self, state = None ):

		if state is None:
			return self.active
		else:
			self.active = state
			self.box.visible = state


	def write( self, msg ):

		self.lines.append( msg )

		# Rotate out the oldest line if the ring is full
		if len( self.lines ) > self.numVisibleLines:
			self.lines.popleft()

		self.editing( True )
		self.update()


	def commitLine( self ):

		# Send the line of input as a chat message
		BigWorld.player().cell.say( unicode( self.editString ) )

		# Display it locally and clear it
		self.write( "You say: " + self.editString )
		self.editString = ""


	def update( self ):

		if self.active is False:
			return

		self.box.text.text = ""

		# Redraw all lines in the ring
		for line in self.lines:
			self.box.text.text = self.box.text.text + line + "\n"

		# Draw the edit line
		self.box.text.text = self.box.text.text + "\cffff00ff;" + self.editString + "_" + "\cffffffff;"


	def handleKeyEvent( self, event ):

		if event.isMouseButton():
			return False

		if self.active is False:
			return False

		if event.isKeyDown():
			if event.key == Keys.KEY_ESCAPE:
				self.editing( False )
			elif event.key == Keys.KEY_RETURN:
				if len( self.editString ) == 0:
					self.editing( False )
				else:
					self.commitLine()
			elif event.key == Keys.KEY_BACKSPACE:
				self.editString = self.editString[:len( self.editString ) - 1]
			elif event.character is not None:
				self.editString = self.editString + event.character

			self.update()
			return True

		return False


# ChatConsole.py
