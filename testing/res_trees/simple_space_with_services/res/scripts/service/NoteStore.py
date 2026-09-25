import BigWorld
import service_utils

import NoteDataStore

from twisted.internet import defer

class NoteStore( BigWorld.Service ):
	def addNote( self, description ):
		deferred = defer.Deferred()
		# Convert single return value to a sequence.
		deferred.addCallback( lambda noteID: (noteID,) )
		NoteDataStore.addNote( description, deferred.callback )
		return deferred

	def getNotes( self ):
		print "NoteStore.getNotes:"
		deferred = defer.Deferred()
		# Convert single return value to a sequence.
		deferred.addCallback( lambda notes: (notes,) )
		NoteDataStore.getNotes( deferred.callback )

		return deferred

service_utils.addStandardWatchers( NoteStore )

# NoteStore.py
