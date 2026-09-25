##
## This script implements WorldEditor's Perforce wrapper for use with BWLockD.
##
## IMPORTANT NOTE: This script needs to be compiled into a windows executable
## so it can be used by WorldEditor. The executable for this file was generated
## using py2exe (www.py2exe.org).
##

################################################################################
# This file implements the stub for most of perforce(p4)
# commands (except managed) return SUCCESS(0) as to indicate a success
# addfile/addbinaryfile/removefile/commitfile/updatefile can also
# use wildcard file names
################################################################################

# includes
from os import popen4
from os import execv
from os import path
from os import spawnv
from os import P_WAIT
from os import walk
from os import chdir
from sys import argv
from sys import exit
from sys import stdout
from sys import stderr
from re import search

# constants
P4_PATH			=	"C:\\Program Files\\Perforce\\p4.exe"
QUOTED_P4_PATH		=	"\"" + P4_PATH + "\""
FAILURE				=	3
SUCCESS				=	0
MANAGED				=	0
UNMANAGED		       =       1
BATCH_LIMIT	=	128

COMMANDS = ( "check", "addfolder", "addfile", "addbinaryfile", "removefile", "commitfile", "updatefile", "editfile", "revertfile", "updatefolder", "refreshfolder", "managed" )

# this class parses the output of p4 in ztag format
class ZTagParser:
	def __init__( self, str ):
		strs = str.split( '\n' )
		m = {}
		self.values = []
		for str in strs:
			if len( str ) != 0 and str[0] == '.':
				str = str[4:]
				name = str[:str.find(' ')]
				value = str[str.find(' ') + 1:]
				m[name] = value
			else:
				if( len( m ) ):
					self.values.append( m )
					m = {}
		if( len( m ) ):
			self.values.append( m )
			m = {}

	def __len__( self ):
		return len( self.values )

	def __getitem__( self, i ):
		return self.values[ i ]

class ClientSpecParser:
	def __init__( self, str ):
		strs = str.split( '\n' )
		m = {}
		self.values = []
		gotViews = False
		client = ''
		root = ''

		for str in strs:
			if str.startswith( "Client:" ):
				client = str[8:].strip()
			if str.startswith( "Root:" ):
				root = str[6:].strip()

			if not gotViews:
				if str.startswith( "View:" ):
					gotViews = True
				continue

			str = str.strip()
			space = str.find( ' ' )
			if space != -1:
				map = str[space + 1:]
				map = map.rstrip( '.' )
				map = map.rstrip( '*' )
				map = map.replace( '//' + client + '/', root )
				map = map.replace( '/', '\\' )
				self.values.append( map )

	def __len__( self ):
		return len( self.values )

	def __getitem__( self, i ):
		return self.values[ i ]

# this function runs commandLine and returns its output
def exec_with_info( commandLine, input = None ):
	print commandLine
	output = ""
	fds = popen4( commandLine )
	if input != None:
		fds[ 0 ].write( input )
		fds[ 0 ].close()
	if fds[ 1 ]:
		output = ''.join( fds[ 1 ].readlines() )
	return output

# this function returns the client name and owner suitable for this file
def get_client_name( fileOrFolder ):
	client = ["",""]
	clientRoot = ""

	fileOrFolder = fileOrFolder.lower()
	if fileOrFolder[-1:0] != "\\":
		fileOrFolder = fileOrFolder + "\\";

	clients = exec_with_info( QUOTED_P4_PATH + " -ztag clients" )
	ztp = ZTagParser( clients );

	for tags in ztp:
		c = tags["client"]

		c = exec_with_info( QUOTED_P4_PATH + " client -o " + c )
		cs = ClientSpecParser( c )

		for view in cs:
			if fileOrFolder.find( view.lower() ) == 0:
				if len( view ) > len( clientRoot ):
					clientRoot = view
					client[0] = tags["client"]
					client[1] = tags["Owner"]
	if len( client[0] ) == 0 or len( client[1] ) == 0:
		return None
	return client

def get_lines( filename ):
	result = []
	f = open( filename )
	if f:
		lines = f.readlines();
		for line in lines:
			while line[-1:] == '\n' or line[-1:] == '\r':
				line = line[:-1]
			if len( line ):
				result.append( line )
		f.close()
	return result

def get_current_directory():
	return path.abspath("")

def get_current_client():
	return get_client_name( get_current_directory() )

def printUsageAndAbort():
	print "USAGE: p4_stub <" + '|'.join( COMMANDS ) + "> [file list]"
	exit( FAILURE )

def do_command( arguments ):
	print ' '.join( arguments ), '\n'
	stdout.flush()
	if "".join( arguments ).find("*") == -1:
		if spawnv( P_WAIT, P4_PATH, arguments ) != SUCCESS:
			return FAILURE
		return SUCCESS

	walk_set = walk( "" )
	path_set = []
	for it in walk_set:
		path_set.append( it[0] )

	exit_code = SUCCESS
	path = get_current_directory()
	if path[-1:0] != '\\':
		path += '\\'

	for it in path_set:
		chdir( path + it )
		if spawnv( P_WAIT, P4_PATH, arguments ) != SUCCESS:
			exit_code = FAILURE # let it continue

	chdir( path )
	return exit_code

def create_change_list( client, desc ):
	command_line = QUOTED_P4_PATH + " -c " + client[0]
	command_line += " change -i"
	input_text = "Change:new\nClient:" + client[0] + '\n'
	input_text += "User:" + client[1] + '\n'
	input_text += "Status:new\nDescription:" + desc + '\n'
	output = exec_with_info( command_line, input_text )
	match = search( "Change (\d+) created.", output )
	if match != None:
		return int( match.group(1) )
	return -1

def do_open( client, changelist, files ):
	result = SUCCESS
	fs = []
	for file in files:
		fs.append( '\"' + file + '\"' )
	while fs:
		argv = fs[:BATCH_LIMIT]
		fs = fs[BATCH_LIMIT:]
		argv.insert( 0, repr( changelist ) )
		argv.insert( 0, "-c" )
		argv.insert( 0, "reopen" )
		argv.insert( 0, client )
		argv.insert( 0, "-c" )
		argv.insert( 0, QUOTED_P4_PATH )
		if do_command( argv ) != SUCCESS:
			result = FAILURE
	return result

def do_submit( argv ):
	change_list = create_change_list( client, argv[0] )
	if change_list != -1:
		files = get_lines( argv[1] )
		do_open( client[0], change_list, files )
		argv = [ QUOTED_P4_PATH, '-c', client[0], 'submit', '-c', repr( change_list ) ]
		do_command( argv )
		return SUCCESS
	return FAILURE

if __name__ == "__main__":
	if len( argv ) < 2 or not argv[1] in COMMANDS:
		printUsageAndAbort()

	del argv[0]
	command = argv[0]
	del argv[0]

	if command == "check":
		if path.isfile( P4_PATH ):
			print '\n0'
			exit(SUCCESS)
		print 'Cannot find ', P4_PATH
		exit(FAILURE)
	client = get_current_client()
	if client == None:
		print get_current_directory(), "is not in any p4 clients\n"
		exit( FAILURE )
	if command == "addfolder":
		exit(SUCCESS)  # adding folder is not supported in p4
	elif command == "addfile":
		argv.insert( 0, "add" )
	elif command == "addbinaryfile":
		argv.insert( 0, "add" )
	elif command == "removefile":
		argv.insert( 0, "revert" )
		argv.insert( 0, client[0] )
		argv.insert( 0, "-c" )
		argv.insert( 0, QUOTED_P4_PATH )
		do_command( argv )
		del argv[0]
		del argv[0]
		del argv[0]
		del argv[0]
		argv.insert( 0, "delete" )
	elif command == "commitfile":
		exit( do_submit( argv ) )
	elif command == "updatefile":
		argv.insert( 0, "sync" )
	elif command == "editfile":
		argv.insert( 0, "edit" )
	elif command == "revertfile":
		argv.insert( 0, "revert" )
	elif command == "updatefolder":
		argv.insert( 0, "sync" )
	elif command == "refreshfolder":
		exit(SUCCESS) # we needn't refresh folder status for p4
	elif command == "managed":
		if path.isdir( argv[0] ):
			exit(MANAGED)
		argv.insert( 0, "fstat" )
		argv.insert( 0, client[0] )
		argv.insert( 0, "-c" )
		argv.insert( 0, QUOTED_P4_PATH )
		output = exec_with_info( ' '.join( argv ) )
		if output.find( "no such file" ) == -1:
			exit(MANAGED)
		exit(UNMANAGED)
	else:
		printUsageAndAbort()

	argv.insert( 0, client[0] )
	argv.insert( 0, "-c" )
	argv.insert( 0, QUOTED_P4_PATH )

	exit( do_command( argv ) )
