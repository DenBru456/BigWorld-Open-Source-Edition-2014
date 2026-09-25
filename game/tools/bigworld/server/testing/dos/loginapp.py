#!/usr/bin/python

# Standard includes
import socket
import sys
import time
import struct
import md5
import os
import copy
import getopt
import random
import re

# BigWorld includes
try:
	sys.path.append(
		os.environ[ "MF_ROOT" ] +
			"/bigworld/tools/server/pycommon".replace( '/', os.sep ) )
except KeyError:
	print "Warning: MF_ROOT is not set"

from constants import *
import packet
import test
import config

# config.py stuff
PROCESS = "loginapp"
COMPONENT = "LoginInterface"

# From login_interface.hpp
LOGIN_MSG_DIGEST = 0
LOGIN_MSG_PORT = 1

PROBE_KEYS = [ "hostName",
			   "ownerName",
			   "usersCount",
			   "universeName",
			   "spaceName",
			   "latestVersion",
			   "impendingVersion" ]

(MESSAGE_ID_LOGIN,
 MESSAGE_ID_PROBE,
 MESSAGE_ID_FETCH) = range(3)

# From login_interface.hpp::LogOnStatus
class LogOnStatus:
	(NOT_SET,
	 LOGGED_ON,
	 CONNECTION_FAILED,
	 DNS_LOOKUP_FAILED,
	 UNKNOWN_ERROR,
	 CANCELLED,
	 ALREADY_ONLINE_LOCALLY,
	 LOGIN_REJECTED_NO_SUCH_USER,
	 LOGIN_REJECTED_INVALID_PASSWORD,
	 LOGIN_REJECTED_ALREADY_LOGGED_IN,
	 LOGIN_REJECTED_BAD_DIGEST,
	 LOGIN_REJECTED_DB_GENERAL_FAILURE,
	 LOGIN_REJECTED_DB_NOT_READY,
	 LOGIN_REJECTED_ILLEGAL_CHARACTERS,
	 LOGIN_CUSTOM_DEFINED_ERROR) = range(15)

# Standard flags which must be at the beginning of every packet
FLAGS_FIELDS = [ ("flags", 0x0, "=B") ]

# Grep the login protocol version out of login_interface.hpp
_headertxt = open(
	os.path.join( os.environ[ "MF_ROOT" ],
				  "bigworld/src/common/login_interface.hpp" ) ).read()
_match = re.search( "^#define LOGIN_VERSION.*?(\d+)", _headertxt, re.MULTILINE )
LOGIN_VERSION = int( _match.group( 1 ) )

# Fields for the mandatory section of a login packet
LOGIN_FIELDS = [ ("id", MESSAGE_ID_LOGIN, "=B"),
				 ("length", 0x0, ">H"),
				 ("version", LOGIN_VERSION, "=B"),
				 ("username", "u", "64s"),
				 ("password", "p", "64s")
				 ]

# Fields for the (optional) digest section of a login packet
DIGEST_FIELDS = [ ("digest_id", LOGIN_MSG_DIGEST, "=B"),
				  ("digest_size", md5.digest_size, "=B"),
				  ("digest", struct.pack("IIII",0,0,0,0), str(md5.digest_size)+"s")
				  ]

# Fields for the (optional) port section of a login packet
PORT_FIELDS = [ ("port_id", LOGIN_MSG_PORT, "=B"),
				("port_size", 2, "=B"),
				("port", 0, "H")
				]

# Fields for a probe packet
PROBE_FIELDS = [ ("id", MESSAGE_ID_PROBE, "=B") ]

# Fields for a fetch packet
FETCH_FIELDS = [ ("id", MESSAGE_ID_FETCH, "=B"),
				 ("version", 0, "I"),
				 ("identifier", 0, "I"),
				 ("offset", 0, "I"),
				 ("length", 0, "I")
				 ]

class Login( packet.Handshake ):
	"""Tests the login() handler in loginapp."""

	def __init__( self, **kwargs ):

		packet.Packet.__init__( self, FLAGS_FIELDS + LOGIN_FIELDS )
		
		# Set all given fields
		for name, value in kwargs.items():
			self.set( name, value )

		self.correctLength()

	def correctLength( self ):
		"""Sets the length field in the header of this packet to the correct
		   value for the actual size of the packet."""
		
		self.set( "length", len( self ) - 4 )
		return self

	def handleReply( self, flags, msgid, length, replyid, data ):
		"""Handle replies to a login packet."""

		# Stream off first status byte
		(status,) = struct.unpack( "=B", data[0] )
		data = data[1:]

		# If login successful
		if status == LogOnStatus.LOGGED_ON:
			(ip, port, salt, sessKey, latestVer, impendingVer) = \
				 struct.unpack( ">IHHIII", data )
			return "success: port %d with session key %x" % (port, sessKey)
		
		# If login failed
		else:
			(length,) = struct.unpack( "=B", data[0] )
			(message,) = struct.unpack( "%ds" % length, data[1:] )
			return "failed: %s" % message

class Probe( packet.Handshake ):
	"""Handler for probe() packets."""

	def __init__( self ):

		packet.Packet.__init__( self, FLAGS_FIELDS + PROBE_FIELDS )

	def handleReply( self, flags, msgid, length, replyid, data ):

		global PROBE_KEYS

		s = ""

		# We expect the data to contain each of the PROBE_KEYS
		for k in PROBE_KEYS:
	
			(keylen,) = struct.unpack( "=B", data[0] ); data = data[1:]
			(key, data) = (data[:keylen], data[keylen:])
			if not data: return
			
			(valuelen,) = struct.unpack( "=B", data[0] ); data = data[1:]
			(value, data) = (data[:valuelen], data[valuelen:])
			if not data: return
			
			# Sanity checking
			if keylen != len( key ) or valuelen != len( value ) or key != k:
				return
				
			s += "%s:%s " % (key, value)

		return s

class Fetch( packet.Handshake ):
	"""Handler for fetch() packets."""

	def __init__( self, **kwargs ):
		
		packet.Packet.__init__( self, FLAGS_FIELDS + FETCH_FIELDS )
		
		# Set all given fields
		for name, value in kwargs.items():
			self.set( name, value )

	def handleReply( self, flags, msgid, length, replyid, data ):

		# Extract status byte
		(ok,) = struct.unpack( "=B", data[0] ); data = data[1:]

		# Error
		if ok == 1:
			return "Fetch handler reported general error"

def basic():
	return [

		# Packet is single byte with valid fields, should be no reply
		packet.Packet( FLAGS_FIELDS ),

		# Invalid flags this time
		packet.Packet( FLAGS_FIELDS, flags = ~FLAGS_OK ),
		
		# Login section with 0 length (this will crash loginapp.cpp version 1.12)
		Login( length = 0 ),
		
		# Basic login section,  too short
		Login( length = 100 ),
		
		# Basic login section, correct length
		Login(),
		
		# Login section with replyID set
		Login( flags = FLAG_HAS_REQUESTS ).
		insert( "reqoffset", 0x1, "H" ),
		
		# Basic login section, too long
		Login( length = 133 ),
		
		# Basic login section, incorrect username
		Login( username = "zzz" ),
		
		# Basic login section, incorrect password
		Login( password = "zzz" ),
		
		# Digest section
		Login().
		insertChunk( DIGEST_FIELDS ).
		correctLength(),
		
		# Port section
		Login().
		insertChunk( PORT_FIELDS ).
		correctLength(),
		
		# Both
		Login().
		insertChunk( DIGEST_FIELDS ).
		insertChunk( PORT_FIELDS ),#.set("length",147),
		
		# Probe message (correct)
		Probe(),
		
		# Probe message (incorrect length)
		Probe().insert( "foo","bar","s" ),
		
		# Fetch message
		Fetch()
		
		]

def knownbaddies():

	return [
		
		# Truncated header for digest footer
		Login().
		insert( "pad", [0], "=B" ).
		set( "length", 130 ),
		
		# Faked length in digest footer
		Login().
		insert( "pad", [0,16], "=BB" ).
		set( "length", 131 ),

		# Overflow in variable size length
		packet.Packet().
		insertChunk( FLAGS_FIELDS ).
		insert( "id", 0xfe, "=B" ).
		insert( "length", 0x80000000, "I" ),

		# Login section with 0 length
		Login( length=0 ),

		# Login name uses '<' which will corrupt an xml database
		Login().
		set( "username", "<OhImBaaaaaad" )
		
		]

def request():

	return [ Login().addReplyId() ]

def loginSuccessful( replies ):

	for r in replies:
		if "success" in r:
			return True
	return False

def ok( sock, process, component ):

	pack = Login().set( "username", str( random.random() ) ).addReplyId()
	return test.testReply( pack, sock, process, component, loginSuccessful )

