"""
Classes etc for uid<->username mapping
"""
import logging
import os

import cluster

log = logging.getLogger( __name__ )


# -----------------------------------------------------------------------------
# Section: Exported interface
# -----------------------------------------------------------------------------

def getCurrentUID():
	if os.name == "posix":
		return os.getuid()
	else:
		id = os.getenv( 'UID' )
		if not id:
			log.info( 'UID environment parameter not set' )
			id = 0
		else:
			id = int( id )
		return id


def getuid( name = None, machine = None ):
	return query( "uid", name, machine )


def getname( uid = None, machine = None ):
	return query( "name", uid, machine )


def query( ret, name = None, machine = None ):
	"""
	Resolve name <-> uid, or get effective uid with no args.
	"""

	# Kwargs to pass to cluster.Cluster() to avoid spamming as much as possible
	kw = {}

	# Convert name to int if possible
	try:
		name = int( name )
		kw[ "uid" ] = name
	except:
		pass

	if name is None:
		name = getCurrentUID()
		kw[ "uid" ] = name

	user = cluster.cache.get( **kw ).getUser( name, machine )
	if user:
		if ret == "uid":
			return user.uid
		else:
			return user.name
	else:
		raise Exception( "Couldn't resolve %s to a uid" % name )


def getall( machines = [] ):
	"""
	Get a list of all users on the cluster.
	"""

	return cluster.cache.get().getAllUsers( machines )

# uid.py
