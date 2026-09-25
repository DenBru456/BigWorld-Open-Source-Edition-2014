import os
import sys
import time
import socket

import bwsetup; bwsetup.addPath( "../.." )

MF_ROOT = os.path.abspath( bwsetup.appdir + "/../../../../.." )

LOGDIR = "/tmp/build-logs"
if not os.path.isdir( LOGDIR ):
	os.makedirs( LOGDIR )
LOGFILE = "%s/build-%s.log" % (LOGDIR, time.strftime( "%Y-%m-%d-%H%M" ))
HOSTNAME = socket.gethostbyaddr( socket.gethostname() )[0].split( "." )[0]
if os.path.exists( LOGFILE ):
	os.unlink( LOGFILE )

def run( cmd, returnLines=False ):
	outputs = []
	f = open( LOGFILE, "a" )
	pipe = os.popen( "%s 2>&1" % cmd )
	line = pipe.readline()
	while line:
		echo( line.rstrip() )
		if returnLines == True:
                        outputs.append( line )
		line = pipe.readline()
	return ((pipe.close() == None), outputs)

def echo( s = "" ):
	print s
	open( LOGFILE, "a" ).write( s + "\n" )

def fail():
	echo()
	echo( "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^" )
	echo( "!!! Aborting due to previous errors !!!" )
	sys.exit( 1 )
