#!/usr/bin/env python

import logging
import messages
import select
import socket
import socketplus
import struct
import sys
import time

from machine import Machine

if __name__ == "__main__":
	import util
	util.setUpBasicCleanLogging()

log = logging.getLogger( __name__ )


# Stolen from the timeit module
if sys.platform == "win32":
	# On Windows, the best timer is time.clock()
	default_timer = time.clock
else:
	# On most other platforms the best timer is time.time()
	default_timer = time.time


def pingRing( timeout = 10 ):
	"""
	Verifies the response time of the machines on the network, as visible by
	broadcast and buddy ring.

	This is a static method because we need to avoid going via refresh() (since
	this is essentially what we are checking).

	This can take up to timeout * (machines+1) if every machine replies as late
	as possible.
	"""

	# Generate a test packet
	packet = messages.MGMPacket()
	message = messages.WholeMachineMessage()
	packet.append( message )
	port = messages.MachineGuardMessage.MACHINED_PORT

	# We store all IPs in A format (i.e. string dotted quad)

	# Mappings of { IP -> clockTime }
	broadcastReplyTimes = {}
	directSendTimes = {}
	directReplyTimes = {}

	# Mapping of { IP -> [ clockTime ] }
	# Only from broadcasts
	dupeReplyTimes = {}

	# Mapping of { IP -> replyBlob }
	replyBlobs = {}

	# Mapping of { IP -> Machine or None }
	knownMachines = {}

	sock = socketplus.socket( "bm" )
	sendBlob = packet.get()
	broadcastSendTime = default_timer()
	sock.sendto( sendBlob, ("<broadcast>", port) )

	# Listen for replies until timeout passes
	# Opencoded socketplus.recvAll plus timestamps
	ready = select.select( [sock], [], [], timeout )[0]
	while ready:
		now = default_timer()
		replyBlob, (srcip, _) = sock.recvfrom( socketplus.RMEM_MAX )
		if srcip in broadcastReplyTimes:
			if srcip not in dupeReplies:
				dupeReplyTimes[ srcip ] = []
			dupeReplyTimes[ srcip ].append( now )
		else:
			broadcastReplyTimes[ srcip ] = now
			replyBlobs[ srcip ] = replyBlob
		ready = select.select( [sock], [], [], timeout )[0]

	if len( replyBlobs ) == 0:
		log.warning( "No replies to broadcast message" )
		return True

	# Set of IPs yet to be directly queried
	targets = set()

	# Process the reply data into knownMachines
	# and collect initial targets
	for srcip, data in replyBlobs.items():
		replyPacket = messages.MGMPacket()
		replyPacket.set( data )
		buddyip = socket.inet_ntoa( struct.pack( "I", replyPacket.buddy ) )
		knownMachines[ srcip ] = Machine( None, replyPacket.messages[0], srcip )
		if replyPacket.buddy != 0 and not knownMachines.has_key( buddyip ):
			knownMachines[ buddyip ] = None

	# Free up some memory, we don't care about these anymore
	del replyBlobs

	targets.update( knownMachines.keys() )

	# Now try each machine directly, one by one.
	while len( targets ) != 0:
		target = targets.pop()
		sock = socketplus.socket( "m" )
		sendBlob = packet.get()
		directSendTimes[ target ] = default_timer()
		sock.sendto( sendBlob, (target, port) )
		if not select.select( [sock], [], [], timeout )[0]:
			continue
		replyBlob, (srcip, _) = sock.recvfrom( socketplus.RMEM_MAX )
		directReplyTimes[ srcip ] = default_timer()
		replyPacket = messages.MGMPacket()
		replyPacket.set( replyBlob )
		buddyip = socket.inet_ntoa( struct.pack( "I", replyPacket.buddy ) )
		if knownMachines[ srcip ] is None:
			knownMachines[ srcip ] = Machine( None, replyPacket.messages[0], srcip )
		if replyPacket.buddy != 0 and not knownMachines.has_key( buddyip ):
			knownMachines[ buddyip ] = None
			targets.add( buddyip )

	# Get a nice sorted list of known machine IPs
	knownIPs = sorted( knownMachines.keys(),
				   key = lambda ip: \
				   struct.unpack( "I", socket.inet_aton( ip ) )[0] )

	for ip in knownIPs:
		if broadcastReplyTimes.has_key( ip ):
			broadcastTime = "%0.3fms" % ((broadcastReplyTimes[ ip ] - broadcastSendTime) * 1000,)
		else:
			broadcastTime = "*"

		if directReplyTimes.has_key( ip ):
			directTime = "%0.3fms" % ((directReplyTimes[ ip ] - directSendTimes[ ip ]) * 1000,)
		else:
			directTime = "*"

		if knownMachines[ ip ] is None:
			machineName = "<Unknown>"
		else:
			machineName = knownMachines[ ip ].name

		if dupeReplyTimes.has_key( ip ):
			dupeCount = ", %d duplicate answers" % ( len( dupeReplyTimes[ ip ] ), )
		else:
			dupeCount = ""

		log.info( "%-15s %-12s Broadcast: %8s, Direct: %8s%s",
			ip, machineName, broadcastTime, directTime, dupeCount )

	return True

if __name__ == "__main__":
	import sys
	sys.exit( not pingRing() )

# ping_ring.py
