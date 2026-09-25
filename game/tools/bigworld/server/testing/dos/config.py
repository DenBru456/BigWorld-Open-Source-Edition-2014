import copy
import pickle
import socket

from constants import *

# All the stuff below is used when actually running this script
DEFAULTS = { 'module': "loginapp",
			 'testfunc': "test" }

KEYS = ( "module",
		 "testfunc",
		 "ip",
		 "port",
		 "process",
		 "component" )

# Hash where all config options go
config = copy.copy( DEFAULTS )

def has_key( k ):
	global config
	return config.has_key( k )

def get( k ):
	global config
	return config[ k ]

def set( k, v ) :
	global config
	config[ k ] = v
	
def all():
	global config
	return config

def dump( name ):
	global config

	# Write a test file that describes the settings used.
	f = open( "%s.txt" % name, "w" )
	for k, v in config.items():
		f.write( "%s: %s\n" % (k, v) )
	f.close()

	# Dump a pickle file for exact loading
	pickle.dump( config, open( "%s.pcl" % name, "w" ),
				 pickle.HIGHEST_PROTOCOL )

def load( filename ):

	# Read pickle file (ignoring text file)
	global config
	config = pickle.load( open( filename, "r" ) )
