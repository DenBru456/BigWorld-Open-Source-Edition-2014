import BigWorld

class Account( BigWorld.Entity ):
	def __init__( self ):
		BigWorld.Entity.__init__( self )
		self.avatarList = None

	# --- Logon  ---
	def failLogon( self, message ):
		return False

	# --- Character list ---
	def printCharacterList( self ):
		for ( aname, atype ) in avatarList:
			print 'Character Name: %s, Character Type %s' %( aname, atype )

	def initCharacterList( self, clist ):
		self.avatarList = clist
		if len(self.avatarList) == 0:
			self.createNewCharacter( self.accountName, self.switchCharacterTo )
		else:
			self.switchCharacterTo( self.avatarList[0]['name'] )

	def switchCharacterTo( self, res, msg ):
		self.base.characterBeginPlay( self.avatarList[0]['name'] )

	def createNewCharacter( self, characterName, callback ):
		self.base.createNewAvatar( str( characterName ) )
		self.createCharacterRequesterCallback = callback

	def createCharacterCallback( self, succeded, msg, newCharacterList ):
		if succeded:
			self.avatarList = newCharacterList
		self.createCharacterRequesterCallback( succeded, msg )

class PlayerAccount( Account ):
	def handleKeyEvent( self, isDown, key, mods ):
		pass


# Account.py
