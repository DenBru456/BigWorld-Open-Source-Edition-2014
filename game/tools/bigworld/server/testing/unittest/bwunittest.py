# Utilities for unit testing BigWorld server

import os
import time
import socket
import pickle
import libxml2
import MySQLdb
import shutil
import unittest

import bwsetup; bwsetup.addPath( "../../" )
from pycommon import bwconfig
from pycommon import messages
from pycommon import cluster
from pycommon import run_script
from pycommon import uid
from pycommon import util
from message_logger import util as mlutil
from message_logger import message_log
from message_logger import mlcat

TEST_RES = os.path.dirname( os.path.abspath( __file__ ) ) + os.sep + "res"

SYNC_DB = os.path.dirname( os.path.abspath( __file__ ) ) + os.sep +  \
				"../../../../bin/Hybrid/commands/sync_db"

# [Groups] in /etc/bwmachined.conf
GROUP = None
MACHINE_NAME = None

# ------------------------------------------------------------------------------
# Section: Server-to-PyUnit Glue
# ------------------------------------------------------------------------------

class TestCase( unittest.TestCase ): pass


RETURN_TO_PYUNIT_CODE = \
"""class ReturnToPyUnit( object ):
 def __init__( self, ip, port ):
  self.ip = ip
  self.port = port
 def __call__( self, val ):
  import socket
  import pickle
  sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
  sock.connect( (self.ip, self.port) )
  sock.sendall( pickle.dumps( val ) )
  sock.close()

returnToPyUnit = ReturnToPyUnit( '%(ip)s', %(port)s )\n
"""

def generateScript( funcs, ip, port ):
	"""
	This method generates the script to run on the server. The first
	function in funcs list is the entry function.
	"""
	script = RETURN_TO_PYUNIT_CODE % { "ip":ip, "port":port }

	# Add functions
	for func in funcs:
		script += funcToString( func )

	# Add entry code
	script += "try:\n"
	script += " %s()\n" % funcs[0].__name__
	script += "except Exception, e:\n"
	script += " returnToPyUnit( e )\n"

	return script


def funcToString( func ):
	"""
	This method returns a function's code as a string. Blank lines
	are ignored and tabs are reduced to a single space.
	"""
	# Code location
	code = func.func_code
	filename = code.co_filename
	lineno = code.co_firstlineno

	# Read source file
	f = file( filename, 'r' )
	lines = f.readlines()
	f.close()

	# Indents in function header
	header = lines[lineno - 1]
	headerIndents = len( header ) - len( header.lstrip() )

	# Generate string
	str = header.lstrip()
	for i in range( lineno, len( lines ) ):
		line = lines[i].expandtabs( 1 )
		lstripped = line.lstrip()
		indents = len( line ) - len( lstripped )

		# Check if still in code block
		if indents <= headerIndents and len( line ) > 1:
			break

		# Ignore blanks lines
		if len( line ) == 1:
			continue

		# Offset to header indents
		str += line[headerIndents:]

	return str + "\n"


def runOnServer( funcs, procName ):
	"""
	This method execute functions on the server and listen
	for a result. The first element in funcs is the entry
	function.
	"""
	c = cluster.Cluster()
	me = c.getUser( uid.getuid() )

	if not me.serverIsRunning():
		raise Exception( "Server not running!" )

	# Start listening for reply
	sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	sock.bind( ('',0) )
	sock.listen( 5 )
	ip, port = sock.getsockname()
	ip = socket.gethostbyname( socket.gethostname() )

	# Printing to stdout will help debugging test case errors
	script = generateScript( funcs, ip, port )

	proc = me.getProcExact( procName )

	# Errors are due to unreliable watchers, retry a few time
	isOK = False
	for i in range( 0, 10 ):
		if run_script.runscript( [proc], script ):
			isOK = True
			break
		time.sleep( 1 )

	if not isOK:
		raise Exception( "Could not send script to the server" )

	# Wait for reply
	newsock, client_addr = sock.accept()

	reply = ""
	data = newsock.recv(512)
	while data:
		reply += data
		data = newsock.recv(512)
	newsock.close()

	val = pickle.loads( reply )

	# Check for server side exceptions
	if isinstance( val, Exception ):
		class ServerSideException( Exception ): pass
		raise ServerSideException( "%s\n%s" % (val.message, script) )

	return val


# ------------------------------------------------------------------------------
# Section: Server Configuration
# ------------------------------------------------------------------------------

def configureServer( configs, entities ):
	"""
	This method configures the server resources and creates a
	temporary database.
	"""
	for filename, doc in bwconfig.configChain:
		backup( filename )

	if configs:
		for c in configs:
			bwconfig.set( c, configs[c] )

	if entities:
		insertEntities( entities )
		insertAlias()

	createTempDB()


def restoreServer():
	"""
	This methods restores all backups files, removes inserted files
	and	the temporary database. It will revert all changes done by
	configureServer().
	"""
	deleteTempDB()

	backups = []
	inserts = []

	dirs = bwconfig.resPaths()

	# For performance restrict to selected sub dirs
	subDirs = ["server", "scripts"]
	dirs = ["%s%s%s" % (dir, os.sep, sub) for sub in subDirs for dir in dirs]
	dirs = [d for d in dirs if os.path.isdir( d )]

	# Iterate resource tree for backuped and inserted files
	while len( dirs ) > 0:
		dir = dirs.pop()

		# Check dir contents
		for lastpart in os.listdir( dir ):
			if lastpart.find( "svn" ) != -1: continue

			fullPath = os.path.join( dir, lastpart )

			if os.path.isdir( fullPath ):
				dirs.append( fullPath )
			elif os.path.isfile( fullPath ):
				if fullPath.endswith( "bwunittest.bak" ):
					backups.append( fullPath )
				if fullPath.endswith( "bwunittest.ins" ):
					inserts.append( fullPath )

	# Revert modified with backup
	for b in backups:
		noext = b.replace( ".bwunittest.bak", "" )
		shutil.move( b, noext )

	# Remove inserted file and its indicator
	for i in inserts:
		noext = i.replace( ".bwunittest.ins", "" )
		if os.path.isdir( i ):
			shutil.rmtree( i )
			shutil.rmtree( noext )
		elif os.path.isfile( i ):
			os.remove( i )
			os.remove( noext )

			# Remove any *.pyc
			pyc = noext.replace( ".py", ".pyc" )
			if os.access( pyc, os.F_OK ):
				os.remove( pyc )


def insertAlias():
	"""
	This method inserts data type aliases.
	"""
	# Aliases to insert
	srcAliasXml = bwconfig.find( "scripts/entity_defs/alias.xml", [TEST_RES] )

	if not srcAliasXml:
		return

	# Current aliases
	dstAliasXml = bwconfig.find( "scripts/entity_defs/alias.xml" )
	backup( dstAliasXml )

	srcDoc = libxml2.parseFile( srcAliasXml )
	dstDoc = libxml2.parseFile( dstAliasXml )

	srcRoot = srcDoc.children
	dstRoot = dstDoc.children

	# Add all aliases in src to dst
	aliasNode = srcRoot.children
	while aliasNode != None:
		if aliasNode.type == "element":
			dstRoot.addChild( aliasNode )
		aliasNode = aliasNode.next

	dstDoc.saveFile( dstAliasXml )


def insertEntities( entities ):
	"""
	This method adds entities to entities.xml, inserts their
	def and script files into the resource tree.
	"""
	entitiesXml = bwconfig.find( "scripts/entities.xml" )
	backup( entitiesXml )

	doc = libxml2.parseFile( entitiesXml )
	rootNode = doc.xpathEval( "/root" )[0]

	files = []

	for e in entities:
		# Add entry to entities.xml
		node = rootNode.addChild( libxml2.newNode( e ) )

		# Script files
		scriptParts = ["base", "cell", "client", "bot"]
		for part in scriptParts:
			files.append( "scripts/%s/%s.py" % ( part, e ) )

		# Def file
		defFile = "scripts/entity_defs/%s.def" % e
		files.append( defFile )

	doc.saveFile( entitiesXml )

	insertFiles( files )


def createTempDB():
	"""
	This method creates a temporary database.
	"""
	dbType = bwconfig.get( "dbApp/type" )

	if dbType == "mysql":
		dbName = os.environ['USER'] + "_bwunittest"

		bwconfig.set( "dbApp/databaseName", dbName )

		dbHost = bwconfig.get( "dbApp/host" )
		dbUser = bwconfig.get( "dbApp/username" )
		dbPass = bwconfig.get( "dbApp/password" )

		conn = MySQLdb.connect(	host = dbHost, user = dbUser, passwd = dbPass )
		cursor = conn.cursor()
		cursor.execute( "CREATE DATABASE %s" % dbName )
		cursor.close()
		conn.commit()
		conn.close()

		os.system( SYNC_DB + " 2> /dev/null" )
	else:
		db = bwconfig.find( "scripts/db.xml" )
		backup( db )
		os.remove( db )

		lines = [ "<db.xml>", "</db.xml>" ]
		f = open( db, "w" )
		f.writelines( lines )
		f.close()


def deleteTempDB():
	"""
	This method deletes the temporary database.
	"""
	dbType = bwconfig.get( "dbApp/type" )

	# XML database is restored by restoreServer
	if dbType == "mysql":
		dbName = os.environ['USER'] + "_bwunittest"
		dbHost = bwconfig.get( "dbApp/host" )
		dbUser = bwconfig.get( "dbApp/username" )
		dbPass = bwconfig.get( "dbApp/password" )

		conn = MySQLdb.connect(	host = dbHost, user = dbUser, passwd = dbPass )
		cursor = conn.cursor()

		try:
			cursor.execute( "DROP DATABASE %s" % dbName )
		except: pass

		cursor.close()
		conn.commit()
		conn.close()

# ------------------------------------------------------------------------------
# Section: Server Startup/Shutdown
# ------------------------------------------------------------------------------

def startServer( layout = None, configs = None, entities = None, layoutXML = None):
	"""
	This method starts a server.

	The layout parameter is a 2D array in the format: [machine][proc].
	If None is given, the layout is a single machine with minimum processes.

	For example:
	[ [baseappmgr, cellappmgr, dbapp, loginapp], [baseapp, cellapp] ]

	Gives:
	bw01: {"baseappmgr", "cellappmgr", "dbapp", "loginapp"}
	bw02: {"baseapp", "cellapp"}

	The configs parameter is a dictionary of bw.xml configurations.

	For example:
	{ "dbApp/secondaryDatabase/enable":"true", "dbApp/port":"3306" }

	The entities parameter is a list entities to insert. Defs and scripts
	found in TES_RES are automatically inserted, an entry in entities.xml
	is automatically added, and TEST_RES/scripts/entity_defs/aliases.xml
	is merged with MF_ROOT/fantasydemo/scripts/entity_defs/aliases.xml

        The layoutXML parameter is a string pointing to a XML layout file.
        If layout parameter is set, layoutfile parameter will be ignored.
        If None are given,  the layout is a single machine with minimum processes
        unless layout parameter is given.

        For example:
        "layout/layout.xml"

	"""
	c = cluster.Cluster()
	me = c.getUser( uid.getuid(), fetchVersion = True )

	if me.serverIsRunning():
		raise Exception( "Server already running" )

	minProcs = ["baseapp",
				"cellapp",
				"dbapp",
				"cellappmgr",
				"baseappmgr",
				"loginapp"]

	if layout == None and layoutXML == None:
		layout = [ minProcs ]

	if os.path.isfile( layoutXML ) == False:
		layout = [ minProcs ]	

	if layout != None:

		# Check for minimum processes
		procs = [p for m in layout for p in m]
		procs =  filter( lambda p: p in procs, minProcs )
		hasMinLayout = len( procs ) == len( minProcs )

		# Check for enough machines
		machines = getMachines( c )
		hasMinMachines = len( machines ) >= len( layout )

		# Do nothing
		if not hasMinLayout or not hasMinMachines:
			return

		configureServer( configs, entities )

		# Start procs on specified machines
		for i in range( 0, len( layout ) ):
			m = layout[i]
			machine = machines[i]

			# Start procs
			pids = [machine.startProc( p, uid.getuid() ) for p in m]

			# Wait till they've started up
			allDone = lambda: None not in [machine.getProc( pid ) for pid in pids]
			c.waitFor( allDone, 1, 10 )

	elif layoutXML != None:

		configureServer( configs, entities )

		me.startFromXML( layoutXML )

	# Let it ramp up
	for i in range( 0, 60 ):
		if not me.serverIsRunning():
			time.sleep( 1 )


def stopServer( shouldRestore = True ):
	"""
	This method stops the server.
	"""
	c = cluster.Cluster()
	me = c.getUser( uid.getuid() )

	if me.serverIsRunning():
		functor = util.Functor(	me.layoutIsStopped,	args = [me.getLayout()],
								kwargs = {"_async_": None} )

		# Controlled shutdown only if loginapp is present
		loginapps = me.getProcs( "loginapp" )
		if loginapps:
			for p in loginapps:
				p.stop( messages.SignalMessage.SIGUSR1 )
		c.waitFor( functor, 1, 20 )

		# Kill any remaining procs
		for p in me.getProcs():
			p.stop( messages.SignalMessage.SIGINT )
		c.waitFor( functor, 1, 20 )

		for p in me.getProcs():
			p.stop( messages.SignalMessage.SIGQUIT )
		c.waitFor( functor, 1, 20 )

	if shouldRestore:
		restoreServer()


def setWatcher( proc, path, value ):
	"""
	This method set watcher value.
	"""
	c = cluster.Cluster()
	me = c.getUser( uid.getuid() )

	# Set watcher values for procs
	for p in me.getProcs( proc ):
		p.setWatcherValue( path, value )


def startProc( proc ):
	"""
	This method starts a server process.
	"""
	c = cluster.Cluster()
	machine = getMachines( c )[0]
	pid = machine.startProc( proc, uid.getuid() )

	done = lambda: machine.getProc( pid ) != None
	c.waitFor( done, 1, 10 )


def stopProc( procName, isKill = False ):
	c = cluster.Cluster()
	me = c.getUser( uid.getuid() )
	proc = me.getProcExact( procName )

	if isKill:
		proc.machine.killProc( proc )
	else:
		proc.stopNicely()

	for i in range( 0, 60 ):
		c.refresh()
		if me.getProcExact( procName ) == None:
			return True
		time.sleep( 1 )

	return False


def getMachines( cluster ):
	"""
	This method get candidate machines on the cluster.
	"""
	if GROUP:
		machines = cluster.getMachines()
		machines.sort( lambda m1, m2: cmp( m1.totalmhz(), m2.totalmhz() ) )

		cluster.queryTags( "Groups" )
		machines = [m for m in machines \
					if "Groups" in m.tags and GROUP in m.tags[ "Groups" ]]
	else:
		global MACHINE_NAME
		if not MACHINE_NAME:
			MACHINE_NAME = socket.gethostname()

		machines = [cluster.getMachine( MACHINE_NAME )]

	return machines


# ------------------------------------------------------------------------------
# Section: Misc Helpers
# ------------------------------------------------------------------------------

def backup( src ):
	"""
	This method backups up file. Backup files are suffixed
	with ".bwunittest.bak".
	"""
	if os.access( src, os.F_OK ):
		dst = "%s.bwunittest.bak" % src

		if os.access( dst, os.F_OK ):
			raise Exception( "Overwritting an unrestored backup: %s" % dst )

		shutil.copy( src, dst )


def insertFiles( files ):
	"""
	This method inserts resource files into the resource tree.
	Inserted files are indicated by a file with the same path
	appended with a ".bwunittest.ins" suffix.
	"""
	for file in files:
		src = "%s/%s" % (TEST_RES, file)

		if not os.access( src, os.F_OK ):
			continue

		# Insert into first path in res tree
		dst = "%s/%s" % (bwconfig.resPaths()[0], file)

		# Backup if already existing, create indicator otherwise
		if os.access( dst, os.F_OK ):
			backup( dst )
		else:
			open( "%s.bwunittest.ins" % dst, "w" ).close()

		shutil.copy( src, dst )


def executeRawDatabaseCommand( cmd ):
	"""
	This method executes a command on the database and returns the results.
	"""
	dbHost = bwconfig.get( "dbApp/host" )
	dbName = bwconfig.get( "dbApp/databaseName" )
	dbUser = bwconfig.get( "dbApp/username" )
	dbPass = bwconfig.get( "dbApp/password" )

	conn = MySQLdb.connect(
			host = dbHost, user = dbUser, passwd = dbPass, db = dbName )
	cursor = conn.cursor()

	cursor.execute( cmd )
	results = cursor.fetchall()

	cursor.close()
	conn.commit()
	conn.close()

	return results 


def isMessageInLog( message, tfrom = None, verbose = False):
	"""
	This method returns True if message can be found on message logger. 
	It only search for current uid.
	""" 
	mlog = message_log.MessageLog()
	options = mlutil.getBasicOptionParser()
	options.uid = os.getuid()

	try:
		options.uid = int( options.uid )
	except:
		try:
			options.uid = mlog.getUsers()[ options.uid ]
		except KeyError:
			log.error( "log %s does not have entries for user %s",
				mlog.root, options.uid )
			sys.exit( 1 )

	kwargs = dict ( uid = options.uid )
	kwargs [ "message" ] = message

	if tfrom is not None:
		parseTime( tfrom, "start", kwargs )

	query = mlog.fetch( **kwargs )

	flag = False 
	for result in query:
		if verbose:
			# Print out the searched string to stdout with columns flag
			cflags = message_log.bwlog.SHOW_MESSAGE + message_log.bwlog.SHOW_PROCS
			mlog.write( result, cflags )
		flag = True

	return flag 


def parseTime( s, name, kw ):
	return mlcat.parseTime( s, name, kw) 

