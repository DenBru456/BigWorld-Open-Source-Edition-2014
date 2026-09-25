# It is possible to run the NoteDataStore example as a Service on ServiceApps.
# This means that the BaseApps do not need to connect to the Note database. It
# will query the Service instead.
RUN_AS_SERVICE = False

import BigWorld

import logging

log = logging.getLogger( "NoteStore" )

if BigWorld.isServiceApp or not RUN_AS_SERVICE:
	from NoteDataStoreImpl import *
else:
	def init( config_file ):
		log.info(  "NoteDataStore is implemented using a service" )

	def addNote( description, callback ):
		deferred = BigWorld.services[ "NoteStore" ].addNote( description )
		deferred.addCallback( lambda results: callback( *results ) )

	def getNotes( callback ):
		deferred = BigWorld.services[ "NoteStore" ].getNotes()
		deferred.addCallback( lambda results: callback( *results ) )

# NoteDataStore.py
