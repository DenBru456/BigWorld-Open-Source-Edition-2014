"""This module implements console commands.

Each function in this module corresponds to a console command. To add another
console command just add a function with the correct prototype.
"""

import BigWorld
import FantasyDemo
import Avatar
import Math
import FDGUI
import re

#def smsnum( player, string ):
#	"Set the SMS number for the player."
#
#	print "Number '" + string + "'"
#	player.cell.setPhoneNumber( string )

#def sms( player, string ):
#	"Send an SMS to the targetted player. If no player is targetted, send to self."
#	if BigWorld.target():
#		BigWorld.target().cell.sendSMS(
#			player.playerName + ": " + string )
#	else:
#		player.cell.sendSMS( string )
#	print "Sending '" + string + "'"

#def group( player, string ):
#	"Send a chat message to all group members."
#
#	# TODO: Prepending the player name is a bit of a hack.
#	player.base.groupChat( string )
#	FantasyDemo.addChatMsg( -1, "Group - you say: " + string )

#def gls( player, string ):
#	"List the players in your current group."
#	player.base.groupList()

#def fls( player, string ):
#	"List your current friends."
#	player.base.friendsList()

#def local( player, string ):
#	"Send a local chat message (e.g. all players at the table)"

#	if player.mode == Avatar.Avatar.MODE_SEATED:
#		# TODO: Why is modeTarget stored as an int?
#		BigWorld.entity(player.modeTarget).cell.tableChat( string )
#		FantasyDemo.addChatMsg( player.id, "[local] " + string )
#	else:
#		# TODO: This may mean a short range chat when not seated?
#		print "Should be seated for local chat."


def who( player, string ):
	"List all online players near you."
	playerList = "Players near you:\n"
	for i in BigWorld.entities.values():
		if i.__class__.__name__ == "Avatar":
			playerList = playerList + i.playerName + "\n"
	FantasyDemo.addChatMsg( -1, playerList )


def help( player, string ):
	"Display help a console command."
	if string:
		try:
			func = globals()[ string ]
			if callable( func ) and func.__doc__:
				for s in func.__doc__.split( "\n" ):
					FantasyDemo.addChatMsg( -1, s )
			else:
				raise "Not callable"
		except:
			FantasyDemo.addChatMsg( -1, "No help for " + string )
	else:
		isCallable = lambda x : callable( globals()[x] )
		ignoreList = ("getV4FromString","help")
		notIgnored = lambda x : x not in ignoreList

		keys = filter( isCallable, globals().keys() )
		keys = filter( notIgnored, keys )
		keys.sort()

		FantasyDemo.addChatMsg( -1, "/help {command} for more info." )

		stripper = lambda c : not c in "[]'\""
		string = filter( stripper, str(keys) )

		FantasyDemo.addChatMsg( -1, string )


def target( player, string ):
	"Send a chat message to the targeted player"
	t = BigWorld.target()

	if t:
		try:
			t.cell.directedChat( player.id, string )
			FantasyDemo.addChatMsg( player.id, "[To " + t.playerName + "] " + string )
		except:
			pass


def pushUp( player, string ):
	"This is the same as pressing the pushUp key."
	player.pushUpKey()


def pullUp( player, string ):
	"This is the same as pressing the pullUp key."
	player.pullUpKey()


def follow( player, string ):
	"Follow the current target"
	if BigWorld.target() != None:
		player.physics.chase( BigWorld.target(), 2.0, 0.5 )
		player.physics.velocity = ( 0, 0, 6.0 )


def summon( player, string ):
	"Summon an instance of the specified entity type on the server at the "
	"present location of the connected/proxy entity"

	typeName = str( string )

	# Properties passed in here must be added to entity_defs/alias.xml
	# Fill in some defaults
	from GameData import CreatureData
	from GameData import SeatData
	from GameData import GuardData
	import AvatarModel
	properties = { 'creatureType': int( CreatureData.UNKNOWN ),
		'creatureName': "Summoned " + typeName,
		'creatureState': int( CreatureData.ALIVE ),
		'seatType': int( SeatData.UNKNOWN ),
		'guardType': int( GuardData.HIGHLANDS_GUARD ),
		'avatarModel' : AvatarModel.pack( AvatarModel.defaultModel() ) }

	# /summon Chicken, Striff etc
	if (typeName in CreatureData.displayNames.values()):
		typeIds = CreatureData.displayNames.items()
		typeId = (key for key,value in typeIds if value==typeName).next()
		properties['creatureType'] = int( typeId )
		typeName = "Creature"

	# /summon Seat
	if (typeName in SeatData.displayNames.values()):
		typeIds = SeatData.displayNames.items()
		typeId = (key for key,value in typeIds if value==typeName).next()
		properties['seatType'] = int( typeId )
		typeName = "Seat"

	# /summon Highlands Guard, Minspec Guard
	if (typeName in GuardData.GUARD_TYPES.values()):
		typeIds = GuardData.GUARD_TYPES.items()
		typeId = (key for key,value in typeIds if value==typeName).next()
		properties['guardType'] = int( typeId )
		model = GuardData.GUARD_MODELS[ typeId ]\
			.createInstanceWithRandomCustomisations()
		properties['avatarModel'] = AvatarModel.pack( model )
		typeName = "Guard"

	# /summon Guard, Pedestrian
	if (typeName in GuardData.GUARD_SHOWNAMES.values()):
		typeIds = GuardData.GUARD_SHOWNAMES.items()
		typeId = (key for key,value in typeIds if value==typeName).next()
		properties['guardType'] = int( typeId )
		model = GuardData.GUARD_MODELS[ typeId ]\
			.createInstanceWithRandomCustomisations()
		properties['avatarModel'] = AvatarModel.pack( model )
		typeName = "Guard"

	if isinstance( BigWorld.connectedEntity(), Avatar.Avatar ):
		BigWorld.connectedEntity().cell.summonEntity( typeName, properties )
	else:
		if (BigWorld.player() is not None and
			isinstance( BigWorld.player(), Avatar.Avatar )):
			BigWorld.player().summonEntity( typeName, properties )
		else:
			FantasyDemo.addChatMsg( -1,
				"Summon can only be called when player is an Avatar" )


def weather( player, string ):
	"Summon a weather system by name"
	import Weather
	Weather.weather().toggleRandomWeather( False )
	Weather.weather().summon( str(string) )


def getV4FromString( string ):
	tokens = string.split(" ")
	v = [1,1,1,1]
	for i in tokens:
		try:
			v.append( float(i) )
		except:
			pass
	return Math.Vector4(v[-4:])


def fog( player, string ):
	"Set the fog colour and density, from 1 (normal) to 10 (very dense)"
	import Weather
	Weather.weather().fog( getV4FromString(string) )


def ambient( player, string ):
	"Set the ambient colour"
	import Weather
	Weather.weather().ambient( getV4FromString(string) )


def sunlight( player, string ):
	"Set the sunlight colour"
	import Weather
	Weather.weather().sun( getV4FromString(string) )



# ------------------------------------------------------------------------------
# Section: Gestures
# ------------------------------------------------------------------------------

def wave( player, string ):
	"Makes the player wave."
	player.playGesture( 1 )

def laugh( player, string ):
	"Makes the player laugh."
	player.playGesture( 16 )

def cry( player, string ):
	"Makes the player cry."
	player.playGesture( 3 )

def point( player, string ):
	"Makes the player point."
	player.playGesture( 24 )

def shrug( player, string ):
	"Makes the player shrug."
	player.playGesture( 4 )

def yes( player, string ):
	"Makes player's head shake."
	player.playGesture( 19 )

def no( player, string ):
	"Makes player's head shake."
	player.playGesture( 20 )

def beckon( player, string ):
	"Makes the player beckon."
	player.playGesture( 21 )

# ------------------------------------------------------------------------------
# Section: Player state
# ------------------------------------------------------------------------------

def fat( player, string ):
	"Makes the player fat."
	player.model.Fat()

def skinny( player, string ):
	"Makes the player skinny."
	player.model.Skinny()


# ------------------------------------------------------------------------------
# Section: Friends List
# ------------------------------------------------------------------------------


def addTransportAccount( player, string ):
	"""Associates a legacy transport account with the users XMPP account.
Format: /addTransportAccount  <transport>   <username>   <password>

Example:
 /addTransportAccount   msn  bigworld@hotmail.com   sup3r$ecr37"""

	# Make sure we turn the Unicode string into a utf-8 encoded string
	string = string.encode( "utf8" ).strip()

	m = re.match( r"(.+?)\s+(.+?)\s+(.+)", string )
	if not m:
		FantasyDemo.addChatMsg( -1, "Invalid transport registration details.",
				FDGUI.TEXT_COLOUR_SYSTEM )
		return

	transport = m.group( 1 )
	username  = m.group( 2 )
	password  = m.group( 3 )
	registerMsg = "Attempting to register %s account %s." % \
						(transport, username)
	FantasyDemo.addChatMsg( -1, registerMsg , FDGUI.TEXT_COLOUR_SYSTEM )
	player.base.xmppTransportAccountRegister( transport, username, password )


def delTransportAccount( player, string ):
	"""Disassociates a legacy transport account from the users XMPP account.
Format: /delTransportAccount  <transport>

Example:
 /delTransportAccount   msn"""

	# Make sure we turn the Unicode string into a utf-8 encoded string
	transport = string.encode( "utf8" ).strip()

	# Check if we know about the transport
	wasFound = False
	for transportDetails in player.xmppTransportDetails:
		if not wasFound and transportDetails[ "transport" ] == transport:
			wasFound = True

	if not wasFound:
		FantasyDemo.addChatMsg( -1, "Transport not known.",
				FDGUI.TEXT_COLOUR_SYSTEM )

	else:
		player.base.xmppTransportAccountDeregister( transport )


def addFriend( player, string ):
	"""Adds a friend to player's friends list.
Format: /addFriend [<Game friend name> | <IM friend name[:protocol]>]

In-game friends (other Avatars)
 /addFriend        - Adds the currently targeted friend.
 /addFriend Alice  - Adds the Avatar with playerName 'Alice' as a friend.

Instant Message friend (XMPP)
 /addFriend bob@   - Adds the XMPP friend 'bob@<xmpp.domain.com>' as a friend.
 /addFriend clive@eval.bigworldtech.com

Instant Message friend (MSN / other transports)
 /addFriend damien@hotmail.com:msn"""

	# Strings containing an '@' will be treated as an IM friend
	if string.find( "@" ) >= 0:
		transport = "xmpp"

		if string.startswith( "@" ):
			FantasyDemo.addChatMsg( -1, "Invalid IM friend name.",
				FDGUI.TEXT_COLOUR_SYSTEM )
			return

		# If there is a transport specified then separate it now
		imContents = string.rsplit( ":", 1 )

		friendID = imContents[ 0 ]
		if len( imContents ) == 2:
			transport = imContents[ 1 ].encode( "utf8" ).lower()


		# TODO: This should be pushed onto the base where we know about the
		#       hostname for the current connection.
		#       Advantage of doing it here:
		#       * quick response to the user on known friend
		#		* roster is not known on base entity
		if friendID.endswith( "@" ):
			friendID += "eval.bigworldtech.com"

		# If the user has provided a full domain to use, check that they
		# aren't already a friend. 
		friendsList = player.roster.findFriendsLike( friendID, transport )
		if len( friendsList ):
			FantasyDemo.addChatMsg( -1, "%s is already a friend." % friendID,
				FDGUI.TEXT_COLOUR_SYSTEM )
			return

		player.base.xmppAddFriend( friendID, transport )

	# All other input is treated as an 'in game' friend.
	else:
		player.addFriend( unicode( string ) )


def delFriend( player, string ):
	"""Deletes a friend from player's friends list.
Format: /delFriend [<friend name>]

In-game friends (other Avatars)
 /delFriend        - Removes the currently targeted friend.
 /delFriend Alice  - Removes the Avatar with playerName 'Alice' as a friend.

Instant Message friends
 /delFriend bob@   - Removes the XMPP friend 'bob@<xmpp.domain.com>'.
 /delFriend clive@eval.bigworldtech.com"""

	friendsList = player.roster.findFriendsLike( string )

	# If the user doesn't exist in our XMPP roster, pass it to the in game
	# friends list.
	if not len( friendsList ):
		player.delFriend( unicode( string ) )

	else:

		if len( friendsList ) > 1:
			FantasyDemo.addChatMsg(	-1,
				"Found multiple friends that match '%s'.",
					FDGUI.TEXT_COLOUR_SYSTEM )
			for friendItem in friendsList:
				FantasyDemo.addChatMsg(	-1, friendItem[ 0 ],
					FDGUI.TEXT_COLOUR_SYSTEM )

		else:
			friend = friendsList[ 0 ]
			player.base.xmppDelFriend( friend[ 0 ], friend[ 1 ] )


def infoFriend( player, string ):
	"Gets information about a friend."
	player.infoFriend( string )


def listFriends( player, string ):
	"Lists your friends (and their online status)."
	player.listFriends()


def msgFriend( player, string ):
	"""Sends a message to a friend.
Format: /msgFriend [<friend name>] : <message> (Note the ':')

In game friends (other Avatars)
 /msgFriend : Hello        - Sends a message to the currently targeted Avatar.
 /msgFriend Alice : Hello  - Sends a message to the Avatar with playerName 'Alice'.

Instant Message friends
 /msgFriend bob@ : Hello to you
 /msgFriend clive@eval.bigworldtech.com : Hello XMPP
 /msgFriend damien@hotmail.com : Hello MSN"""

	words = string.split( ":", 1 )
	if len( words ) < 2:
		FantasyDemo.addChatMsg(	-1,
			"Invalid format - /help msgFriend for details",
			FDGUI.TEXT_COLOUR_SYSTEM )
		return

	recipient = words[ 0 ].strip()
	message = words [ 1 ].strip()

	if not len( message ):
		FantasyDemo.addChatMsg(	-1,
			"Invalid format - /help msgFriend for details",
			FDGUI.TEXT_COLOUR_SYSTEM )
		return

	friendsList = player.roster.findFriendsLike( recipient )

	# If the user doesn't exist in our XMPP roster, pass it to the in game
	# friends list.
	if not len( friendsList ):
		player.msgFriend( unicode( recipient ), message )

	else:

		if len( friendsList ) > 1:
			FantasyDemo.addChatMsg(	-1,
				"Found multiple friends that match '%s'.",
					FDGUI.TEXT_COLOUR_SYSTEM )
			for friendItem in friendsList:
				FantasyDemo.addChatMsg(	-1, friendItem[ 0 ],
					FDGUI.TEXT_COLOUR_SYSTEM )

		else:
			friend = friendsList[ 0 ]
			player.base.xmppMsgFriend( friend[ 0 ], friend[ 1 ], message )

			recipient = friend[ 0 ] + " [IM]"

	FantasyDemo.addChatMsg(	-1, "You say to " + recipient + ": " + message,
							FDGUI.TEXT_COLOUR_YOU_SAY )


tell = msgFriend
t = msgFriend

# ------------------------------------------------------------------------------
# Section: Features
# ------------------------------------------------------------------------------
def teleport( player, dst ):
	"""Teleport to a location.
Format: /teleport <space> <location>

Example:
 /teleport spaces/highlands WatchTower"""

	# Try splitting on ' ' then '/'.
	# e.g. spaces/highlands demo1
	# e.g. spaces/highlands/demo1
	try:
		spaceName, pointName = str(dst).rsplit( ' ', 1 )
	except ValueError:
		try:
			spaceName, pointName = str(dst).rsplit( '/', 1 )
		except ValueError:
			return

	BigWorld.player().tryToTeleport( spaceName, pointName )
	FantasyDemo.rds.fdgui.chatWindow.script.hideNow()


# ------------------------------------------------------------------------------
# Section: External Data Stores Examples
# ------------------------------------------------------------------------------
def addNote( player, description ):
	"Adds a note to the external note data store."

	if description == None or len( description ) == 0:
		FantasyDemo.addChatMsg( -1, "Must provide a note description" )
	else:
		print "Adding a note:", description
		player.base.addNote( unicode( description ) )


def getNotes( player, arg ):
	"Retrieves a list of notes from the external notes data store."

	player.base.getNotes()

# ------------------------------------------------------------------------------
# Section: Aliases
# ------------------------------------------------------------------------------

# The following are aliases for commands.
#l = local
#g = group
#t = tell
