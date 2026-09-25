import BigWorld
import FantasyDemo

import Util
import sys

from TextInputPage import TextInputPage
from functools import partial

import random
import re

SIGNIN_PATTERN = re.compile( r'bigworld://launch/(?P<game_public_key>[0-9]+)/(?P<gamer_id>[0-9]+)/(?P<signin_key>.*)' )

if hasattr( random, "SystemRandom" ):
	randrange = random.SystemRandom().randrange
else:
	randrange = random.randrange

def validUsername( value ):
	return value.strip() != ""


class ConnectToServerPage( TextInputPage ):
	caption = "Enter Username:"

	def __init__( self, menu, host, label ):
		TextInputPage.__init__( self, menu )
		self.host = host
		self.label = label

	def pageActivated( self, reason, outgoing ):
		TextInputPage.pageActivated( self, reason, outgoing )

		signin_params = BigWorld.commandLineLoginInfo()

		if signin_params:
			user_id, signin_key = signin_params
			self.onEnter( user_id, signin_key )
		else:
			self.setText( FantasyDemo.rds.li.username )
			self.onTextChanged( self.getText() )

	def onEnter( self, value, password='pass' ):		
		username = value.strip()
		if not validUsername( username ):
			return

		rds = FantasyDemo.rds
		rds.userPreferences.writeWideString( 'lastUsedAccountName', unicode(username) )
		rds.userPreferences.write( 'lastServer', '' )

		for i in BigWorld.serverDiscovery.servers:
			if FantasyDemo._serverNetName( i ) == self.host:
				'''
				Although only the uid is currently used. The full server
				info is saved for completeness and to assist in debugging.
				'''
				rds.userPreferences.writeString(	'lastServer/hostName',		i.hostName )
				rds.userPreferences.writeString(	'lastServer/ip',			Util.serverDottedHost( i.ip ) )
				rds.userPreferences.writeString(	'lastServer/ownerName',		i.ownerName )
				rds.userPreferences.writeInt(		'lastServer/port',			i.port )
				rds.userPreferences.writeString(	'lastServer/spaceName',		i.spaceName )
				rds.userPreferences.writeInt(		'lastServer/uid',			i.uid )
				rds.userPreferences.writeString(	'lastServer/universeName',	i.universeName )
				rds.userPreferences.writeInt(		'lastServer/usersCount',	i.usersCount )

		BigWorld.savePreferences()

		# The personality script will be responsible for setting up the 
		# connection status text as well as the appropriate menu's post-connect.
		FantasyDemo.connectToServer( self.host, self.label, username, password )

	def onTextChanged( self, value ):
		self.enableOK( validUsername(value) )


# ConnectToServer.py
