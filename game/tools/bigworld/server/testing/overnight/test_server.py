#!/usr/bin/env python

import sys
import re

import bwsetup; bwsetup.addPath( "../.." )

from common import *
import build_server
from pycommon import cluster
from pycommon import util

import os
import socket
import logging
log = logging.getLogger( __name__ )


print "Running:", ' '.join( sys.argv )
print "User:", os.environ['USER']
print "Machine:", socket.gethostname()

try:
	MACHINE = sys.argv[1]
except:
	import socket
	MACHINE = socket.gethostname()

# Shutdown the server
me = cluster.Cluster().getUser( fetchVersion = True )
if not me.smartStop():
	log.error( "Couldn't shut down server nicely" )

if not me.smartStop( forceKill = True ):
	log.error( "Couldn't force kill the server" )

# Build the server
build_server.main()
echo()

# Manually sync tables to defs
# TODO: Remove when dbapp can auto syncTablesToDefs
run( "%s/bigworld/bin/Hybrid%s/commands/sync_db" % (MF_ROOT, build_server.architecture) )


if False:
	# Run regression tests
	echo( util.border( "Running regression tests" ) )
	os.chdir( "%s/bigworld/tools/server/testing/unittest/" % MF_ROOT )
	run( "./test_runner.py" )
	echo()

# Restart the server
echo( util.border( "Restarting server" ) )
os.chdir( "%s/bigworld/tools/server" % MF_ROOT )
run( "./control_cluster.py start %s" % MACHINE )
