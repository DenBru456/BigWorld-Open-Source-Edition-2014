#!/usr/bin/python

import os
import time
import socket
import copy
import sys
import getopt
import select
import random
import string
import types
import struct

# BigWorld includes
try:
	sys.path.append(
		os.environ[ "MF_ROOT" ] +
			"/bigworld/tools/server/pycommon".replace( '/', os.sep ) )
except KeyError:
	print "Warning: MF_ROOT is not set"

import messages
import config
import packet
import util
import cluster
import uid as uidmodule

def discoverTarget( component ):
	"""Queries bwmachined for any IP address the named component is running
	   on."""

	mgm = messages.MachineGuardMessage()
	mgm.message = mgm.FIND_MESSAGE
	mgm.param = mgm.PARAM_USE_CATEGORY | mgm.PARAM_USE_NAME | mgm.PARAM_USE_UID
	mgm.category = mgm.SERVER_COMPONENT
	mgm.name = component
	mgm.uid = os.getuid()

	sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	sock.sendto( mgm.get(), ("<broadcast>", mgm.MACHINED_PORT) )

	while select.select( [ sock ] , [] , [], 0.2 )[ 0 ]:
	
		(data, (ip, port)) = sock.recvfrom( 1 << 16 )
		mgm.set( data )

		# Just return the first one we find
		tgtport = struct.unpack( "!H", struct.pack( "H", mgm.param ) )[0]
		return (ip, tgtport)

def alive( component ):
	"""Queries bwmachined as to whether the named component is running.  Note
	   that this is a component name such as 'LoginInterface' not a process name
	   such as 'loginapp'."""

	# Message to poll loginapp
	mgm = messages.MachineGuardMessage()
	mgm.message = mgm.FIND_MESSAGE
	mgm.param = mgm.PARAM_USE_CATEGORY | mgm.PARAM_USE_NAME
	mgm.category = mgm.SERVER_COMPONENT
	mgm.name = component

	# Socket for bwmachined queries
	bwmdsock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	bwmdsock.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1 )
	bwmdsock.sendto( mgm.get(), ("<broadcast>", mgm.MACHINED_PORT) )

	# Read bwmachined replies
	while select.select( [ bwmdsock ] , [] , [], 0.1 )[ 0 ]:
		
		(data, (ip, port)) = bwmdsock.recvfrom( 1 << 16 )
		mgm.set( data )

		if mgm.name == component and mgm.uid == os.getuid():
			return True
		
	return False

def respawn( process, component ):

	# Poll for component
	if not alive( component ):

		# Run component
		print "respawning %s ... " % component,; sys.stdout.flush();
		me = cluster.Cluster().getUser( uidmodule.getuid() )
		me.getMachines()[0].startProc( process, me.uid )

		# Wait till it's up before returning
		while not alive( component ):
			time.sleep(1)

		print "back online @", time.ctime()
		sys.stdout.flush()

def handleCrash( packet, replies, process, component ):

	# If we haven't even sent a packet, we've probably just done something silly
	# so don't freak out too much
	if packet == None:
		print "No previous packet, not noting a crash in the logs!"
		return

	# Print info about packet that caused the crash
	print "================================"
	print "!!! server component crashed !!!"
	print
	print packet
	
	if replies:
		print "Replies:"
		for r in replies:
			print r
	else:
		print "No replies!"
		
	# Figure out if there's a corefile associated with this crash
	core, asst = None, None
	for f in [ f for f in os.listdir( "." ) if ("core.%s" % process) in f ]:

		# If so, we'll add the info to the crash log and copy the corefile to
		# the directory
		if time.time() - os.stat( f )[-2] < 5:
			core = f
			os.system( "mv %s %s/%s" % (core, packet.LOGDIR, core) )

			# Move the assert with it as well if it exists
			f = core.replace("core","assert") + ".log"
			if os.access( f, os.F_OK ):
				asst = f
				os.system( "mv %s %s/%s" % (asst, packet.LOGDIR, asst) )

			break

	if core: print core
	if asst: print asst
	print

	# Make a note in the log directory about the packet that caused the crash
	crashstr = "%s @ %s" % (packet.name, time.ctime())
	if core: crashstr += " %s" % core
	if asst: crashstr += " %s" % asst
	crashstr += "\n"
	open( packet.LOGDIR + "/crash", "a" ).write( crashstr )

	# Wait a little for things to settle down
	time.sleep( 5 )

	# Respawn the server component
	respawn( process, component )

def test( packet, sock, process, component ):
	"""Sends the packet on the socket.  If a previous call to this function
	   caused the component to die, then it will be discovered now."""

	# Replies from server
	replies = []

	# If the component is not running, then the previous test must've crashed
	# the server.
	if not alive( component ):
		handleCrash( packet.prevpacket, packet.prevreplies, process, component )

	try:
		replies = packet.send( sock )
		
	# Still need an except here in case server crashes after 'if not alive'
	# block above or bwmachined doesn't know the server's gone down yet.
	except socket.error:
		handleCrash( packet.prevpacket, packet.prevreplies, process, component )

		# Need to send the packet again otherwise it will just be skipped.
		# Really shouldn't get another exception here since we just respawned
		# the server
		replies = packet.send( sock )

	return replies

def testReply( packet, sock, process, component, replyFunc ):
	"""Similar to regular test(), but also takes a function which is called on
	   the list of server replies.  The function should return a boolen
	   indicating whether or not the reply was as expected/acceptable."""

	replies = test( packet, sock, process, component )
	return replyFunc( replies )

def scrambleTest( packet, sock, process, component, repsPerByte = 1):
	"""Given a packet, will send variations on the packet to the server by
	   scrambling each different byte down the line.  repsPerByte variations
	   will be sent for each byte in the packet."""

	for b in range( len( packet ) ):
		for i in range( repsPerByte ):

			# Get a unique copy of this packet
			p = packet.copy()

			# Mangle the specified byte and run normal test procedure
			p.scramble( b )
			test( p, sock, process, component )

def reallyScrambleTest( packet, sock, process, component, prob = 0.5, repsPerByte = None):
	"""Each byte in the packet will be scrambled with probability 'prob' and
	   tested.  If repsPerByte is not specified, the packet will be rescrambled
	   a number of times equal to its size."""

	if repsPerByte == None: repsPerByte = len( packet )

	for r in range( repsPerByte ):

		# Copy packet
		p = packet.copy()

		# Traverse packet and scramble some bytes
		for b in range( len( p ) ):
			if random.random() < prob:
				p.scramble( b )

		# Send packet off
		test( p, sock, process, component )

def reorderTest( packet, sock, process, component ):
	"""Each field in the packet is randomly move to another index."""

	for fname in packet.order:

		# Copy packet
		p = packet.copy()

		# Extract field and delete from packet
		field = p[ fname ]
		p.delete( fname )

		# Reinsert at random index
		r = random.randrange( len( p.order ) + 1 )
		p.insert( field.name, field.values, field.fmt, r )

		# Send packet
		test( p, sock, process, component )

def allTestsWithDefaults( packet, sock, process, component ):
	"""Do all tests.  Takes time linear in the packet size at the moment."""

	test( packet, sock, process, component )
	scrambleTest( packet, sock, process, component )
	reallyScrambleTest( packet, sock, process, component )
	reorderTest( packet, sock, process, component )

USAGE = """Commands:
  --packetfunc FUNC           Execute FUNC from the module for the process we
                              are testing which should return a list of packet
                              objects, which are then sent to the server using
                              whichever test is active.
  --packets [FILES]           Recreate packets from given pickle files and
                              send to server
  --replay DIR[,first[,last]] Resend packets from DIR in order, optionally
                              starting from 'first' and ending at 'last'.  This
                              automatically loads all config options from that
                              directory's log file as well, however any cmdline
                              config options will override the loaded ones.
  --cleanup DIR               Remove all unnamed log directories from DIR
  --template PROC             Use config template for the given process.
  
Configuration (defaults given in parentheses):
  --module MODULE             Use MODULE.py as the test module (%s)
  --ip ADDR                   Destination ip address (from module)
  --port PORT                 Destination port (from module)
  --testfunc TEST             Use function TEST to send packets to server (%s)

Available tests:
%s""" \
% (
   config.DEFAULTS["module"],
   config.DEFAULTS["testfunc"],
   string.join( [ "    %s\n" % k for (k, v) in globals().items() if
				  ("test" in k or "Test" in k) and
				  type( v ) == types.FunctionType ], '' )
   )

ARGS = "packetfunc= packets sanity replay= cleanup= " + \
	   "module= ip= port= testfunc= help"

def testSanity( testmodule, sock, process, component ):
	"""Quick sanity test for a given module."""

	# Spend one second flushing all incoming packets out of the stream, as there
	# may be leftovers from previous tests
	while select.select( [sock], [], [], 1 )[0]:
		sock.recvfrom( 1 << 16 )

	return alive( component ) and \
			   getattr( testmodule, "ok" )( sock, process, component )

def main():

	# Parse args
	try:
		opts, files = getopt.getopt( sys.argv[1:], "", ARGS.split() )
	except getopt.GetoptError, e:
		print "Unrecognised arg: %s\n" % e.opt
		print USAGE
		return 1

	# Print help if asked for
	if not opts:
		print USAGE
		return 0
	
	for opt, arg in opts:
		if opt == "--help":
			print USAGE
			return 0

	# Use override config options
	for opt, arg in opts[:]:
		if opt[2:] in config.KEYS:
			config.set( opt[2:], arg )
			opts.remove( (opt, arg) )

	# Load up the test module
	testmodule = __import__( config.get( 'module' ) )

	# Set process and component config options from module's globals
	config.set( "process", testmodule.PROCESS )
	config.set( "component", testmodule.COMPONENT )

	# If ip and port not given explicitly on commandline
	tgt = discoverTarget( testmodule.COMPONENT )
	if tgt:
		if not config.has_key( "ip" ): config.set( "ip", tgt[0] )
		if not config.has_key( "port" ): config.set( "port", tgt[1] )

	# Whether or not we've actually sent something
	havesent = False
	sanityCheck = False

	# Get socket to server process
	global sock
	sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
	if config.has_key( 'ip' ):
		sock.connect( (config.get( 'ip' ), int( config.get( 'port' ) ) ) )

	# Process commands
	for opt, arg in opts:

		# Remove all directories that have float names
		if opt == "--cleanup":

			try:
				os.lstat( arg + "/current" )
				os.unlink( arg + "/current" )
			except:
				pass

			for d in os.listdir( arg ):
				try:
					float( d )
					os.system( "rm -rf %s/%s" % (arg, d) )
				except:
					print "Not cleaning up", d

			continue

		# All options below here need the server to be running
		if not alive( config.get( 'component' ) ):
			respawn( config.get( 'process' ), config.get( 'component' ) )
			tgt = discoverTarget( testmodule.COMPONENT )
			config.set( "ip", tgt[0] ); config.set( "port", tgt[1] )
			sock.connect( (config.get( 'ip' ), config.get( 'port' )) )

		havesent = True

		# Do initial sanity test now
		if not sanityCheck:
			
			if not testSanity( testmodule, sock, config.get( 'process' ),
							   config.get( 'component' ) ):
				print "!!! Pre-test sanity check failed - aborting !!!"
				return 1
			else:
				print "* Pre-test sanity check OK"
				sanityCheck = True

		# Replay all packets from a given directory
		if opt == "--replay":

			parts = arg.split( ',' )
			logdir, start, end = parts[0], None, None
			if len( parts ) > 1: start = int( parts[1] )
			if len( parts ) > 2: end = int( parts[2] )

			# Reload configuration from file
			config.load( logdir + "/config.pcl" )

			# Re override any cmdline config options
			opts, files = getopt.getopt( sys.argv[1:], "", ARGS.split() )
			for opt, arg in opts[:]:
				if config.has_key( opt[2:] ):
					config.set( opt[2:], arg )
					opts.remove( (opt, arg) )

			testmodule = __import__( config.get( 'process' ) )
			sock.connect( (config.get( 'ip' ), int( config.get( 'port' ) ) ) )

			# Print config info for run
			print "Configuration for replay is:"
			for k, v in config.all().items():
				print "%12s: %s" % (k, v)
			print
			
			# Get pickle files
			ids = [ f[:-len( ".pcl" )] for
					f in os.listdir( logdir ) if ".pcl" in f ]

			# Filter out non-int ones
			for id in ids[:]:
				try:
					int( id )
				except ValueError:
					ids.remove( id )

			# Put em in order
			ids = [ int( id ) for id in ids ]
			ids.sort()

			# Prune away before start and after end if needed
			for id in ids[:]:
				if (start and id < start) or (end and id > end):
					ids.remove( id )

			# Re-send all old packets
			for id in ids:
				p = packet.Packet.load( logdir + "/" + str( id ) + ".pcl" )
				test( p, sock, config.get( 'process' ), config.get( 'component' ) )

		# Load up all pickle files given on command line and send em to server
		if opt == "--packets":

			for filename in files:
				p = packet.Packet.load( filename )
				test( p, sock, config.get( 'process' ), config.get( 'component' ) )

		# Execute the specified method from the testmodule.  That method should
		# take no arguments and return a list of packets, which are then sent to
		# the server
		if opt == "--packetfunc":

			packetfunc = arg

			# If test given, use it, otherwise fall back on default
			if "," in packetfunc:
				packetfunc, testfunc = packetfunc.split(",")
			else:
				testfunc = config.get( 'testfunc' )

			# Try to get named function
			try:
				packetfuncobj = getattr( testmodule, packetfunc )
				packetfunc = packetfuncobj
			except AttributeError:
				members = map( lambda str: getattr( testmodule, str ),
							   dir( testmodule ) )
				methods = filter( lambda m: type( m ) == types.FunctionType,
								  members )

				print "Unknown test function '%s', possible alternatives:\n" \
					  % packetfunc
				for m in methods: print m.func_name
				return 1
				
			packets = packetfunc(); assert type( packets ) == list;
			testfunc = eval( testfunc )

			# Send all packets to server
			for p in packets:
				testfunc( p, sock, config.get( 'process' ),
						  config.get( 'component' ) )

	# When we're done, we want to test if the server is still ok.
	if havesent and testSanity( testmodule, sock, config.get( 'process' ),
								config.get( 'component' ) ):
		print "* Post-test sanity check OK"
		return 0

	elif havesent:
		print "* Post-test sanity check failed"
		return 1

	else:
		return 0

if __name__ == "__main__":
	util.setUpBasicCleanLogging()

	sys.exit( main() )
