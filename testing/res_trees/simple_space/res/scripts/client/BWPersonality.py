# This is the client personality script for the BigWorld tutorial.  Think of it
# as the bootstrap script for the client.  It contains functions that are called
# on initialisation, shutdown, and handlers for various input events.

import GUI
import BigWorld
import Keys

import chapters

# ------------------------------------------------------------------------------
# Section: Globals
# ------------------------------------------------------------------------------

gChatConsole = None

# ------------------------------------------------------------------------------
# Section: Required callbacks
# ------------------------------------------------------------------------------

# The init function is called as part of the BigWorld initialisation process.
# It receives the BigWorld xml config files as arguments.  This is the best
# place to configure all the application-specific BigWorld components, like
# initial camera view, etc...
def init( scriptsConfig, engineConfig, prefs ):

	if scriptsConfig.readBool( "server/online" ):
		initOnline( scriptsConfig )
	else:
		initOffline( scriptsConfig )

	# Create the chat console and make global reference so we don't have to
	# keep re-acquiring it on each keypress
	global gChatConsole
	from Helpers import ChatConsole
	gChatConsole = ChatConsole.ChatConsole(
		scriptsConfig.readInt( "chat/visibleLines" ) )

	# Hide the mouse cursor and restrict it to the client area of the window.
	GUI.mcursor().clipped = True
	GUI.mcursor().visible = False

# This is called immediately after init() finishes.  We're done with all our
# init code, so this is a no-op.
def start():
	pass


# This method is called just before the game shuts down.
def fini():
	pass


# This is called by BigWorld when player moves from inside to outside
# environment, or vice versa.  It should be used to adapt any personality
# related data (eg, camera position/nature, etc).
def onChangeEnvironments( inside ):
	pass

# This is called by the engine when a system generated message occurs.
def addChatMsg( msg ):
	gChatConsole.write( msg )
# Keyboard event handler
def handleKeyEvent( event ):

	# If the chat console is in edit mode, let it handle all keypresses
	if gChatConsole.editing():
		return gChatConsole.handleKeyEvent( event )

	# If the user hits the ENTER key, we enter chat mode
	if event.isKeyDown() and event.key == Keys.KEY_RETURN:
		gChatConsole.editing( True )
		return True

	return False


# Mouse event handler
def handleMouseEvent( event ):
	return False


# Joystick event handler
def handleAxisEvent( event ):
	return False


# ------------------------------------------------------------------------------
# Section: Helper methods
# ------------------------------------------------------------------------------

def initOffline( scriptsConfig ):

	# Create a space for the client to inhabit
	spaceID = BigWorld.createSpace()

	# Load the space that is named in scripts_config.xml
	BigWorld.addSpaceGeometryMapping(
		spaceID, None, scriptsConfig.readString( "space" ) )

	# Create the player entity, using positions from scripts_config.xml
	playerID = BigWorld.createEntity(
		scriptsConfig.readString( "player/entityType" ),
		spaceID, 0,
		scriptsConfig.readVector3( "player/startPosition" ),
		scriptsConfig.readVector3( "player/startDirection" ),
		{} )

	BigWorld.player( BigWorld.entities[ playerID ] )

def initOnline( scriptsConfig ):

	class LoginParams( object ):
		pass

	def onConnect( stage, step, err = "" ):
		pass

	# Connect to the server with an empty username and password.  This works
	# because the server has been set up to allow logins for any user/pass.
	BigWorld.connect( scriptsConfig.readString( "server/host" ),
					  LoginParams(), onConnect )

# BWPersonality.py
