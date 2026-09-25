import BigWorld
import GUI
import Keys

import collections

class ChatConsole( object ):
	"""
	Leverages the GUI.Console object to provide a basic chat console.
	"""

	sInstance = None

	def __init__( self, numVisibleLines = 4 ):
		"""
		Create a new ChatConsole with a maximum number of visible lines.  Note
		that you cannot construct one of these things until after
		BWPersonality.init() has been called because it relies on resource stuff
		that is initialised prior to init().
		"""

		self.numVisibleLines = numVisibleLines
		self.lines = collections.deque()
		self.timerID = None

		self.con = GUI.Console()
		self.con.editCallback = self.editCallback
		self.con.editPrompt = '> '
		self.con.editCol = 0
		self.con.editRow = numVisibleLines + 1

		self.con.editColour = (255, 128, 64, 255)
		self.con.colour = (255, 255, 255, 255)

		self.con.position = (-1, -1, 0)
		self.con.verticalAnchor = "BOTTOM"
		self.con.horizontalAnchor = "LEFT"

		self.con.cursor = (0, 0)

		GUI.addRoot( self.con )
		ChatConsole.sInstance = self


	@classmethod
	def instance( cls ):
		"""
		Static access to singleton instance.
		"""

		if not cls.sInstance:
			cls.sInstance = ChatConsole()
		return cls.sInstance


	def write( self, msg ):
		"""
		Append a new line of output to the console.
		"""

		self.lines.append( msg )

		# Rotate out the oldest line if the ring is full
		if len( self.lines ) > self.numVisibleLines:
			self.lines.popleft()

		# Redraw all lines in the ring
		self.con.clear()
		for line in self.lines:
			self.con.prints( line + "\n" )

		# Show the console now.
		self.show()

		# If we're not editing, hide the console after 10 seconds.
		if not self.editing():
			self.hide( 10 )


	def hide( self, delay = 0 ):
		"""
		Hide the console in the specified number of seconds, or now if none
		specified.
		"""

		# Cancel any outstanding timers
		if self.timerID is not None:
			BigWorld.cancelCallback( self.timerID )
			self.timerID = None

		if delay == 0:
			self.con.visible = False
		else:
			self.timerID = BigWorld.callback( delay, self.hide )


	def show( self ):
		"""
		Show the console immediately.
		"""

		# Cancel any hide timer
		if self.timerID is not None:
			BigWorld.cancelCallback( self.timerID )
			self.timerID = None

		self.con.visible = True


	def editing( self, val = None ):
		"""
		Enter/leave editing mode if val is passed, otherwise return whether or
		not we're in editing mode.
		"""

		if val is None:
			return self.con.editEnable

		else:
			self.show()
			self.con.editEnable = val


	def editCallback( self, line ):
		"""
		Callback for when a line of input is entered.
		"""

		# Send the line of input as a chat message
		BigWorld.player().cell.say( unicode(line) )

		# Display it in our own console
		self.write( "You say: " + line )

		# Stop editing since the user has pressed ENTER
		self.editing( False )


	def handleKeyEvent( self, event ):

		if event.isKeyDown() and event.key == Keys.KEY_ESCAPE:

			if self.editing():
				self.editing( False )
			else:
				self.hide()

			return True

		else:
			return self.con.handleKeyEvent( event )


# ChatConsole.py
