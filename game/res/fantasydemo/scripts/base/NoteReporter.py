import NoteDataStore

class NoteReporter( object ):
	"""This class manages the interface for note addition and retrieval."""

	def addNote( self, description ):
		NoteDataStore.addNote( description, self.onAddNote )

	def onAddNote( self, id ):
		pass

	def getNotes( self ):
		NoteDataStore.getNotes( self.onGetNotes )

	def onGetNotes( self, noteList ):
		pass


# NoteReporter.py
