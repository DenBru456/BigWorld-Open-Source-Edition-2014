#!/usr/bin/python

import struct
import random
import copy
import string
import socket
import os
import time
import select
import cPickle as pickle
import sys

from constants import *
import util
import config

class Field:
	"""A simple struct to represent the name and default format and values of a
	   packet field."""

	def __init__( self, name, values, fmt ):
		
		# All values must be lists internally
		if type( values ) != list:
			values = [ values ]

		# Set fields
		self.name = name
		self.values = values
		self.fmt = fmt

		# Make sure the values match the format
		self.binary()

	def binary( self ):
		try:
			return struct.pack( *( [self.fmt] + self.values ) )
		except struct.error:
			raise "Format '%s' does not match %s" % (self.fmt, self.values)

	def __len__( self ):
		return len( self.binary() )

	def __str__( self ):
		return "%12s: %s (%s)" % (self.name, self.values, self.fmt)

	def scramble( self, byte=None ):

		# Make a copy of ourselves before we scramble
		oldself = copy.deepcopy( self )

		# If byte unspecified, pick a random byte
		if byte == None:
			byte = random.choice( range( len( self ) ) )

		# Generate a random byte
		r = random.choice( range( 256 ) )
		
		# Form binary string of self, then mangle
		s = self.binary()
		s = s[:byte] + struct.pack("B",r) + s[byte+1:]

		# Recreate self by unpacking mangled string
		newvals = struct.unpack( self.fmt, s )
		for i in range( len( newvals ) ):
			self.values[ i ] = newvals[ i ]

		# Return old self
		return oldself

	def get( self, index = None ):
		"""Return the value from this field at the given index, or all values if
		   no index given."""

		if index == None:
			return self.values

		else:
			return self.values[ index ]
		

class Packet( dict ):
	"""A class to represent a contiguous chunk of data in a packet."""

	# How long we'll wait for the replies from the server for a packet with and
	# without replyid fields, respectively
	REPLY_TIMEOUT_WITH_ID = 0.4
	REPLY_TIMEOUT = 0.2

	# Base directory for logs
	LOGDIR_ROOT = os.environ[ "MF_ROOT" ] + \
				  "/bigworld/tools/server/testing/dos/log"

	# Directory all packets are written to once sent (this is created when the
	# first packet is dump()ed)
	LOGDIR = None

	# Ticker for unique packet id's
	PACKET_ID = 0

	# Whether or not we log on send()
	LOG_ON_SEND = True

	# Static record of previous packet sent and any replies to it
	prevpacket, prevreplies = None, None

	def __init__( self, fields=None, **kwargs ):
		"""Construct a chunk using layout and defaults specified in 'fields'.
		   Assignments given in the kwargs will override defaults."""

		# The list of the names of the fields in this packet, in order
		self.order = []

		# Nothing scrambled originally
		self.scrambled = []

		# Create the first chunk if given
		if fields: self.insertChunk( fields, **kwargs )

	def __str__( self ):
		"""Returns human-readable repr of this packet."""

		# Build heading
# 		title = "%s (%d bytes)" % (self.name, len( self ))
# 		#s = ( "=" * len( title ) ) + ( "\n%s\n\n" % title )
# 		s = title + "\n\n"

		# Add fields
		s = string.join( [str( self[ name ] ) + '\n' for name in self.order] , '' )

		s += "\n%d bytes total\n" % len( self )

# 		# Add record of any scramblings that have happened
# 		if self.scrambled:
# 			s += "\npre-scramble fields:\n"
# 			s += string.join( [ str( f ) + "\n" for f in self.scrambled ], '' )

		return s
				
	def __len__( self ):
		"""Returns the packed size of this chunk."""
		
		return len( self.binary() )

	def binary( self ):
		"""Returns the binary packed version of this chunk."""

		return string.join( [self[ name ].binary() for name in self.order], '' )

	def set( self, name, values, fmt=None ):
		"""Set an _existing_ field using the given values and format.  If format
		   is not given then use the previous format for that field."""

		# Make sure this field is in our order list
		if name not in self.order:
			raise "Setting unknown field '%s'" % name

		# Use format from previous value if format not given
		if fmt == None:
			fmt = self[ name ].fmt

		# Set the field in our internal hash
		self[ name ] = Field( name, values, fmt)
		
		return self
			
	def insert( self, name, values, fmt, index = None ):
		"""Insert an arbitrary field into this chunk at given index.  If index
		   is not given, append new field to end of chunk."""

		# Inserting at the end if no index given
		if index == None: index = len( self.order )

		# Check this field isn't already defined
		if self.has_key( name ):
			raise "Cannot insert duplicate field '%s'" % name

		self.order.insert( index, name )
		self.set( name, values, fmt )
		return self
		
	def insertChunk( self, fields, index = None, **kwargs ):
		"""Add a chunk of fields to this packet at the specified index, or
		   append them to the end of the packet if no index specified.  Fields
		   are filled from the list of tuples in 'fields' and any mappings given
		   in the kwargs will override those given in 'fields'."""

		# Inserting at the end if no index given
		if index == None: index = len( self.order )

		# Go through provided defaults and insert em all
		for (name, values, fmt) in fields:
			self.insert( name, values, fmt, index )
			index += 1
				
		# Overwrite with provided params
		for (name, values) in kwargs.items():

			# If tuple provided, overwrite fmt and values
			if type(values) == tuple:
				(fmt, values) = values
				self.set( name, values, fmt )

			# Otherwise use default fmt and just overwrite values
			else:
				self.set( name, values )

		return self

	def delete( self, name ):
		"""Remove a field from this chunk."""

		try:
			self.order.remove( name )
			del self[ name ]
			return self
		
		except ValueError:
			raise "Cannot remove unknown field '%s' from this chunk" % name

	def chopOff( self, name ):
		"""Remove the field all following fields from this chunk."""

		# Get the position this field occupies
		try:
			i = self.order.index( name )
		except ValueError:
			raise "Cannot chop off unknown field '%s' from this chunk" % name

		# Start chopping things off
		while i < len( self.order ):
			self.delete( self.order[ i ] )

		return self

	def addReplyId( self, replyid = None ):
		"""Adds the required headers and footers to this packet to get a proper
		   round-trip reply id back from the server.  Requires this packet to
		   have 'flags' and 'id' as the first two fields, and optionally a
		   'length' field after the 'id'."""

		# Generate replyid if none given
		if replyid == None:
			replyid = random.randrange( 1 << 32 )

		if len( self.order ) < 1 or self.order[ 0 ] != "flags":
			print "WARNING: Tried to add reply fields to an flag-less packet"
			return

		if len( self.order ) < 2 or self.order[ 1 ] != "id":
			print "WARNING: Tried to add reply fields to an id-less packet"
			return

		# Figure out if there is a length field, if so, we'll insert after it
		if len( self.order ) > 2 and self.order[ 2 ] == "length":
			index = 3
		else:
			index = 2

		# Put in replyid and nextrequestoffset headers
		self.insert( "replyid", replyid, "I", index); index += 1;
		self.insert( "nro_header", 0, "H", index);

		# Put nextrequestoffset footer on
		self.insert( "nro_footer", 1, "H" )

		# Alter flags
		self[ "flags" ].values[ 0 ] |= FLAG_HAS_REQUESTS

		return self

	def send( self, sock, log = None ):
		"""Send this packet via the given socket and write logs."""

		# Send packet and write logs if required
		sock.send( self.binary() )
		if (log == None and self.LOG_ON_SEND) or log == True:

			# Generate unique log name.  We have to do this every time we send the
			# packet so that logs will be replayable (i.e. we need a separate log
			# file for every packet _sent_, as opposed to every packet object
			# created in this process).  Also, this has to be done at this point to
			# get the correct ordering of packet names in the log directory.
			self.name = str( Packet.PACKET_ID )
			Packet.PACKET_ID += 1
			self.dump()

		# Read any server replies
		replies = []

		# If there is a replyid field in this packet, we'll wait a little longer
		# for the server to respond
		if self.has_key( 'replyid' ):
			timeout = self.REPLY_TIMEOUT_WITH_ID
		else:
			timeout = self.REPLY_TIMEOUT

		while select.select( [sock], [], [], timeout )[0]:
			replies.append( sock.recvfrom(1<<16) )
			break

		# Remember this packet and it's replies for crash detection
		Packet.prevpacket = self
		Packet.prevreplies = replies

		return replies
	
	def scramble( self, byte=None ):
		"""If byte unspecified, pick a random field of this chunk and scramble a
	       random byte in it.  If byte specified, then scramble that exact byte
		   of this chunk.  In either case, returns field pre-scramble."""

		# Take random offset into this packet if no byte specified
		if byte == None: byte = random.choice( range( len( self ) ) )

		# Figure out which field we're scrambling
		b = byte
		for name in self.order:
			field = self[ name ]
			if b < len( field ):
				break
			elif name != self.order[-1] :
				b -= len( field )

		# If byte past end of field, then invalid byte offset was given
		if b < 0 or b >= len( field ):
			raise "Invalid byte offset %d into chunk of size %d" % (byte, len( self ))

		# Remember old version of the field we just scrambled
		self.scrambled.append( field.scramble( b ) )

		return self

	def copy( self ):
		"""Returns a deep copy of this packet."""

		return copy.deepcopy( self )

	def dump( self ):
		"""Write logs."""

		# Set up log dir if not done yet
		if Packet.LOGDIR == None:
			while Packet.LOGDIR == None or os.access( Packet.LOGDIR, os.F_OK ):
				Packet.LOGDIR = (Packet.LOGDIR_ROOT + "/" + str( time.time() ))

			# Make sure log root exists
			try:
				os.stat( Packet.LOGDIR_ROOT )
			except:
				print "Log root dir does not exist, mkdir'ing %s" % Packet.LOGDIR_ROOT
				os.mkdir( Packet.LOGDIR_ROOT )

			# Create session log dir
			print "Logging all packets to", \
				  Packet.LOGDIR.replace( os.getcwd()+'/', '' )
			os.mkdir( Packet.LOGDIR )

			# Write command line to log directory
			open( Packet.LOGDIR + "/cmdline", "w" ).\
				  write( string.join( sys.argv ) + "\n" )

			# Write config to log directory
			config.dump( Packet.LOGDIR + "/config" )

			# Set up handy symlink
			linkname = Packet.LOGDIR_ROOT + "/current"
			try:
				os.lstat( linkname )
				os.unlink( linkname )
			except:
				pass
			os.symlink( Packet.LOGDIR, linkname )

		# Log filenames
		binfile = "%s/%s.bin" % (self.LOGDIR, self.name)
		txtfile = "%s/%s.txt" % (self.LOGDIR, self.name)
		pclfile = "%s/%s.pcl" % (self.LOGDIR, self.name)

		# Write files
		open( binfile, "w" ).write( self.binary() )
		open( txtfile, "w" ).write( str( self ) )

		f = open( pclfile, "w" )
		pickle.dump( self, f, pickle.HIGHEST_PROTOCOL )
		f.close()

		# Write any scrambles out too
# 		for field in self.scrambled:
# 			dump( binfile+"."+field.name, field.binary(), "a" )
# 			dump( txtfile+"."+field.name, str( field )+"\n", "a" )

		return self

	def load( self, filename ):
		"""Static method to recreate a packet from a packet name by unpickling it."""

		f = open( filename, "r" )
		p = pickle.load( f )
		f.close()
		return p

	load = classmethod( load )

class Handshake( Packet ):
	"""Fairly trivial extension of packet which provides some decoding of server
	   replies.  Class is virtual in that handleReply() always throws an
	   exception ... derived classes must overload this method with a
	   protocol-specific unpacking method."""

	# Whether we want info about malformed reply packets
	WARNINGS = False
	
	def send( self, sock ):
		"""Send this login packet over the provided socket and decode replies"""

		# Get replies from underlying send() method
		rawreplies = Packet.send( self, sock )
		replies = []

		for (data, (ip, port)) in rawreplies:

			# Break into header and body
			headerfmt = "=BBII"
			header = data[ :struct.calcsize( headerfmt ) ]
			body = data[ struct.calcsize( headerfmt ): ]

			# Split up header section
			try:
				(flags, msgid, length, replyid) = \
						struct.unpack( headerfmt, header )

				# Sanity checking
				if msgid != kReplyMessageIdentifier:
					raise "Received reply message with incorrect header!"

				# Reply-id field handling
				if self.has_key( 'replyid' ):
					if replyid != self[ 'replyid' ].get( 0 ) and self.WARNINGS:
						print "WARNING: replyid mismatch: got %x, wanted %x" % \
							  (replyid, self[ 'replyid' ].get( 0 ) )

				# Pass body to class specific handler
				unpacked = self.handleReply( flags, msgid, length, replyid, body )

				# If handleReply() returns nothing then it didn't understand the message
				if unpacked == None and self.WARNINGS:
					open( "%s/%s.bin.reply" % (self.LOGDIR, self.name), "a" ).\
						  write( body )
					print "WARNING: Mangled body of server reply for:"
					print self

				elif unpacked != None:
					replies.append( unpacked )

			# This comes from the unpack above
			except struct.error:
				if self.WARNINGS:
					open( "%s/%s.bin.reply" % (self.LOGDIR, self.name), "a" ).\
						  write( data )
					print "WARNING: Mangled header of server reply for:"
					print self

		return replies

	def handleReply( self, flags, msgid, length, replyid, data ):
		"""Unpack binary reply data from server. Derived classes must override
		   this."""
		
		raise "Must overload handleReply() method!"
