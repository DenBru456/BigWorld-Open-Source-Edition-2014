##
## This script implements WorldEditor's SVN wrapper for use with BWLockD.
##
## IMPORTANT NOTE: This script needs to be compiled into a windows executable
## so it can be used by WorldEditor. The executable for this file was generated
## using py2exe (www.py2exe.org).
##

import os
import sys
import fnmatch

# neilr: Add local site-packages folder so we can move 3rd party libs to it.
import site
site.addsitedir( "site-packages" )

SUCCESS = 0
FAILURE = 3

try:
	import pysvn
	svn_action = pysvn.wc_notify_action
except ImportError:
	print "ERROR: pysvn is not installed."
	sys.exit( FAILURE )



def recursive_glob( pattern ):
	matches = []
	for root, dirnames, filenames, in os.walk( '.' ):
		for filename in fnmatch.filter( filenames, pattern ):
			fullPath = os.path.normpath( os.path.join( root, filename ) )
			matches.append( fullPath )
	return matches

def status( svnClient, path ):
	return svnClient.status( path, recurse=False, get_all=False )

def cmdCheck( svnClient, args ):
	print '.svn\n1'
	return SUCCESS

def cmdManaged( svnClient, args ):
	try:
		path = os.path.normpath( args[0] )
		statuses = [ s for s in status( svnClient, path ) if s.path == path ]
		if len(statuses) == 0:
			return SUCCESS
		return SUCCESS if statuses[0].is_versioned else FAILURE
	except pysvn.ClientError as e:
		return FAILURE

def cmdAddFile( svnClient, args ):
	try:
		fileList = []
		for pattern in args:
			for file in recursive_glob( pattern ):
				fileList.append( file )
		svnClient.add( fileList )
	except pysvn.ClientError as e:
		print "svn: warning:", str(e)
	return SUCCESS

def cmdAddBinaryFile( svnClient, args ):
	return cmdAddFile( svnClient, args )

def cmdAddFolder( svnClient, args ):
	# args[0] is a message, not used for svn add.
	try:
		svnClient.add( args[1:], recurse=False )
	except pysvn.ClientError as e:
		print "svn: warning:", str(e)
	return SUCCESS

def cmdRemoveFile( svnClient, args ):
	try:
		svnClient.remove( args )
	except pysvn.ClientError as e:
		print "svn: warning:", str(e)
	return SUCCESS

def cmdCommitFile( svnClient, args ):
	message = args[0]
	fileListFile = args[1]
	fileList = [ x.strip() for x in open( fileListFile ).readlines() ]
	try:
		svnClient.checkin( fileList, message )
		return SUCCESS
	except pysvn.ClientError as e:
		print "svn: error:", str(e)
		return FAILURE	

def cmdEditFile( svnClient, args ):
	# Don't do anything for SVN
	return SUCCESS

def cmdRevertFile( svnClient, args ):
	try:
		svnClient.revert( args )
	except pysvn.ClientError as e:
		print "svn: warning:", str(e)
	return SUCCESS

def cmdUpdateFolder( svnClient, args ):
	try:
		svnClient.update( args )
	except pysvn.ClientError as e:
		print "svn: warning:", str(e)
	return SUCCESS

def cmdRefreshFolder( svnClient, args ):
	# Don't do anything for SVN
	return SUCCESS

COMMANDS = {
	"check": cmdCheck,
	"managed": cmdManaged,
	"addfolder": cmdAddFolder,
	"addfile": cmdAddFile, 
	"addbinaryfile": cmdAddBinaryFile,
	"removefile": cmdRemoveFile,
	"commitfile": cmdCommitFile,
	"editfile": cmdEditFile,
	"revertfile": cmdRevertFile,
	"updatefolder": cmdUpdateFolder,
	"refreshfolder": cmdRefreshFolder,
}

def svnNotify( event ):
	PATH_ACTIONS_MAP = {
		svn_action.add: "Added '%s'",
		svn_action.delete: "Deleted '%s'",
		svn_action.revert: "Reverted '%s'",
		svn_action.skip: "Skipped '%s'",
		svn_action.restore: "Restored '%s'",
			
		svn_action.update_update: "U\t'%s'",
		svn_action.update_add: "A\t'%s'",
		svn_action.update_delete: "D\t'%s'",
		
		svn_action.commit_modified: "M\t'%s'",
		svn_action.commit_added: "A\t'%s'",
		svn_action.commit_deleted: "D\t'%s'",
		svn_action.commit_replaced: "R\t'%s'",
		
		svn_action.delete: 'D',
	}
	
	IGNORE_ACTIONS = ( svn_action.commit_postfix_txdelta, )
	
	act = event['action']
	if act == svn_action.update_completed:
		print "Updated to revision %d." % event['revision'].number
	elif act in PATH_ACTIONS_MAP:
		path = os.path.normpath( event['path'] )
		print PATH_ACTIONS_MAP[act] % path
	elif act not in IGNORE_ACTIONS:
		msg = str(act)
		if event['path']:
			msg += ": " + event['path']
		print msg


def printUsage():
	print "USAGE: svn_stub <" + '|'.join( COMMANDS.keys() ) + "> [file list]"


def main():
	if len(sys.argv) < 2:
		printUsage()
		return FAILURE

	cmdName = sys.argv[1]
	args = sys.argv[2:]
	
	cmdFn = COMMANDS.get( cmdName, None )
	if cmdFn is None:
		sys.stderr.write( "ERROR: unknown command '%s'\n" % cmdName )
		printUsage()
		return FAILURE
		
	#print cmdName, args, os.getcwd()

	svnClient = pysvn.Client()
	svnClient.callback_notify = svnNotify
		
	return cmdFn( svnClient, args )


if __name__ == "__main__":
	sys.exit( main() )

