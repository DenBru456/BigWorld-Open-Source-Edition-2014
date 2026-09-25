# 
# NOTE:
#
# There is a known issue with using the BackgroundTaskMgr where performing
# any operation that can modify an Entity's data (for example either property
# set operations or remote method calls) from within the doBackgroundTask()
# method may cause network packet corruption and in turn a process crash.
#
# To avoid this issue, when using Python BackgroundTasks perform all entity
# modifications and interactions from within the doMainThreadTask() callback.
#

import ResMgr

import BackgroundTask

import logging
import os

log = logging.getLogger( "NoteStore" )

try:
	import AsyncSQLAlchemy
	from sqlalchemy import Column, Integer, UnicodeText
	from sqlalchemy.ext.declarative import declarative_base
	import oursql
	hasRequiredModules = True
except Exception, e:
	log.error( "%s", e )
	log.error( "To enable the Note Data Store example please see "
			"fantasydemo/res/server/examples/note_data_store/instructions.txt" )
	hasRequiredModules = False



NOTEREPORTING_THREADS = 5

conn = None
bgTaskMgr = None
isReady = False


def init( config_file ):

	global conn
	if conn != None:
		log.error( "NoteDataStore.init: A connection already exists, failing." )
		return False

	if not hasRequiredModules:
		return False

	status = True

	sec = ResMgr.openSection( config_file )
	if sec == None:
		log.error( "NoteDataStore.init: %s not found.", config_file )
		return False

	enabled = sec.readBool( "enabled", False )
	if enabled == None or enabled == False:
		return False

	dbtype = sec.readString( "database/type" )

	if dbtype == "sqlite":
		dbFile = sec.readString( "database/filename" )

		# If it's an absolute path, then use it as is, otherwise place it
		# relative to the res directory
		if dbFile[ 0 ] != "/":
			dbFile = ResMgr.resolveToAbsolutePath( dbFile ) 

		# TODO: check the file directory actually exists.

		dburi = "%s:///%s" % (dbtype, dbFile)
	else:

		host = sec.readString( "database/host" )
		username = sec.readString( "database/username" )
		password = sec.readString( "database/password" )
		dbname = sec.readString( "database/databaseName" )

		dburi = "%s://%s:%s@%s/%s" % (dbtype, username, password, host, dbname)

	try:
		conn = AsyncSQLAlchemy.SQLAlchemyConnInfo( dburi )

	except Exception, e:
		log.error( "NoteDataStore.init: Failed to init SQLAlchemy: %s", dburi )
		log.error( "%s", e )
		return False

	global bgTaskMgr
	bgTaskMgr = BackgroundTask.Manager( "NoteDataStore" )
	bgTaskMgr.startThreads( NOTEREPORTING_THREADS )

	# Go and load the tables from the DB now
	task = LoadTableTask( conn )
	bgTaskMgr.addBackgroundTask( task )

	return True


def fini():
	global bgTaskMgr
	global conn
	global isReady

	isReady = False

	if bgTaskMgr != None:
		bgTaskMgr.stopAll()
		bgTaskMgr = None

	if conn != None:
		conn = None


def isEnabled():
	return isReady and hasRequiredModules


def createSession():
	return conn.createSession()


#--------------
# Table loading
#--------------
class LoadTableTask( BackgroundTask.BackgroundTask ):
	"""This class creates a new note in the note reporting database."""

	def __init__( self, conn ):

		self.conn = conn


	def doBackgroundTask( self, bgTaskMgr, threadData ):

		session = conn.createSession()
		status = True

		try:
			Note.__table__.create( bind=conn.db_engine, checkfirst=True )
		except Exception, e:
			log.error( "NoteDataStore: Failed to create table: %s", e )
			status = False

		session.close()
		session = None

		global isReady
		isReady = status


#---------------------------
# Database Table definitions
#---------------------------
if hasRequiredModules:
	SQLAlchemyBase = declarative_base()
	class Note( SQLAlchemyBase ):
		__tablename__ = 'notes'

		id = Column( Integer, autoincrement = True,
					nullable = False, primary_key = True )
		description = Column( UnicodeText )


		def __init__( self, description ):
			self.description = unicode( description )


# ------------------------------------------------------------------------------
# Section: Tasks
# ------------------------------------------------------------------------------

try:
	from AsyncSQLAlchemy import warn_exception
except:
	pass


class AddNoteTask( BackgroundTask.BackgroundTask ):
	"""This class creats a new note in the note reporting database."""

	def __init__( self, callback, description ):
		self.callback = callback
		self.description = description
		self.noteId = None
		self.status = None


	def doBackgroundTask( self, bgTaskMgr, threadData ):
		session = createSession()

		# TODO: determine space information / position
		note = Note( self.description )
		session.add( note )

		(self.status, result) = warn_exception( session.flush )
		if self.status:
			self.noteId = note.id
			(self.status, result) = warn_exception( session.commit )

		session.close()

		bgTaskMgr.addMainThreadTask( self )


	def doMainThreadTask( self, bgTaskMgr ):
		assert( self.status != None )

		noteId = 0
		if self.status:
			noteId = self.noteId
		self.callback( noteId )


class GetNoteTask( BackgroundTask.BackgroundTask ):
	"""This class retrieves notes from the note reporting database."""

	def __init__( self, callback ):

		self.callback = callback
		self.status = None
		self.result = []


	def doBackgroundTask( self, bgTaskMgr, threadData ):
		session = createSession()
		query = session.query( Note )

		(self.status, self.result) = warn_exception( query.all )

		session.close()
		session = None

		bgTaskMgr.addMainThreadTask( self )


	def doMainThreadTask( self, bgTaskMgr ):
		assert( self.status != None )

		result = [dict( id = note.id, description = note.description )
				for note in self.result]

		self.callback( result )

# ------------------------------------------------------------------------------
# Section: Functions
# ------------------------------------------------------------------------------

def addNote( description, callback ):
	# Only add a note if the connection the DB has been established and
	# the tables have been reflected.
	if not isEnabled():
		log.notice( "Unable to add note, NoteDataStore isn't ready" )
		return

	task = AddNoteTask( callback, description )
	bgTaskMgr.addBackgroundTask( task )


def getNotes( callback ):

	# Only add a note if the connection the DB has been established and
	# the tables have been reflected.
	if not isEnabled():
		log.notice( "Unable to add note, NoteDataStore isn't ready" )
		return

	task = GetNoteTask( callback )
	bgTaskMgr.addBackgroundTask( task )

# NoteDataStore.py
