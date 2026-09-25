#!/usr/bin/env python

import logging
import memory_stream
import messages
import socket
import socketplus
import struct

from machine import Machine

if __name__ == "__main__":
	import util
	util.setUpBasicCleanLogging()

log = logging.getLogger( __name__ )


def checkRing():
	"""
	Verifies the correctness of the buddy ring on the network.  This is a
	static method because we need to avoid going via refresh() (since that
	is essentially what we are checking).
	"""

	packet = messages.MGMPacket()
	packet.append( messages.WholeMachineMessage() )

	sock = socketplus.socket( "bm" )
	sock.sendto( packet.get(),
				 ("<broadcast>", messages.MachineGuardMessage.MACHINED_PORT) )

	dupeReplies = False

	# Mapping of {ip -> (Machine, buddy ip address)}
	machines = {}

	for data, (srcip, _) in socketplus.recvAll( sock, 1.0 ):
		packet.read( memory_stream.MemoryStream( data ) )

		if srcip not in machines:
			machines[ srcip ] = \
					  (Machine( None, packet.messages[0], srcip ),
					   socket.inet_ntoa( struct.pack( "I", packet.buddy ) ))
		else:
			log.error( "Duplicate reply from %s", srcip )
			dupeReplies = True


	# We deliberately
	ring = sorted( machines.keys(),
				   key = lambda ip: \
				   struct.unpack( "I", socket.inet_aton( ip ) )[0] )

	for ip in ring:

		m, buddyip = machines[ ip ]

		try:
			buddy = machines[ buddyip ][0]
		except KeyError:
			log.info( "%-15s %-12s -> %-15s (non-existent)",
					  m.ip, m.name, buddyip )
			continue

		correctbuddy = machines[
			ring[ (ring.index( ip ) + 1) % len( ring ) ] ][0]

		if buddy == correctbuddy:
			log.info( "%-15s %-12s -> %-15s %-12s",
					  m.ip, m.name, buddy.ip, buddy.name )
		else:
			log.info( "%-15s %-12s -> %-15s %-12s should be %s (%s)",
					   m.ip, m.name, buddy.ip, buddy.name,
					   correctbuddy.ip, correctbuddy.name )
			ok = False

	log.info( "" )

	if dupeReplies:
		log.error( "Some machines on your network are sending duplicate "
				   "replies.  This can indicate that you have dual-NIC "
				   "machines with both interfaces connected to "
				   "the same subnet.\n" )

	if machines:
		curr = machines.keys()[0]
		while machines:

			# TODO fix this
			if curr not in machines:
				log.error( "Ring broken by %s", curr )
				for addr in machines:
					log.error( "%s isn't anyone's buddy", addr )
				return False

			next = machines[ curr ][1]
			del machines[ curr ]
			curr = next

		if not machines:
			log.info( "* Ring is complete *" )

	return True

if __name__ == "__main__":
	import sys
	sys.exit( not checkRing() )

# check_ring.py
