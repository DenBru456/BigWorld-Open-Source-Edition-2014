# This file shows a simple example of using the BigWorld.registerFileDescriptor
# methods.
#
# See bigworld/src/server/baseapp/eg_tcpechoserver.py for an example server.
#
# To run:
# Run the server
# ./eg_tcpechoserver.py 12345
#
# From BaseApp Python console (e.g. "control_cluster.py pyconsole baseapp")
# >>> import TCPEcho
# >>> TCPEcho.echo( "Testing", ("127.0.0.1", 12345) )

import functools
import socket
import BigWorld

def echo( message, addr ):
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	s.setblocking( False )

	# Python's socket.connect method raises an exception when non-blocking
	# informing that the operation is in progress. Catch this and continue.
	try:
		s.connect( addr )
	except:
		pass

	BigWorld.registerWriteFileDescriptor( s,
			functools.partial( onWrite, message ) )

def onWrite( message, s ):
	s.send( message )
	BigWorld.deregisterWriteFileDescriptor( s )
	BigWorld.registerFileDescriptor( s, onRead )

def onRead( s ):
	data = s.recv( 1024 )

	if data:
		print "Received", data
	else:
		BigWorld.deregisterFileDescriptor( s )
		s.close()

# TCPEcho.py
