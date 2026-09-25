#!/usr/bin/env python

from common import *
import struct
import socket
import logging
import threading
import datetime

LOG_FORMAT = "%(asctime)s %(levelname)-6s %(message)s"
log = logging.getLogger( 'bwlockd_test' )

class Lock( object ):
	def __init__( self, rect, computerName, username, desc, lockTime ):
		self.rect = rect
		self.computerName = computerName
		self.username = username
		self.desc = desc
		self.lockTime = lockTime

class BWLockDConnection( object ):
	def __init__( self ):
		self._socket = None

	def connect( self, host, port=8168 ):
		log.info( "Connecting to %s:%d", host, port )
		self._socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self._socket.connect( (host, port) )
		commandCode, failure, payload = self._waitForReply(
			BWLOCKCOMMAND_CONNECT )


	def username( self, username ):
		log.debug( "SETUSER command: %s", username )
		self._sendMsgPacket( BWLOCKCOMMAND_SETUSER, username )
		commandCode, failure, payload = self._waitForReply(
			BWLOCKCOMMAND_SETUSER )

	def setSpace( self, space ):
		log.debug( "SETSPACE command: %s", space )
		self._sendMsgPacket( BWLOCKCOMMAND_SETSPACE, space )
		commandCode, failure, payload = self._waitForReply(
			BWLOCKCOMMAND_SETSPACE )

	def lock( self, rect, lockMsg ):
		log.debug( "LOCK command: %r, %s", rect, lockMsg )
		rectStr = self.packRect( rect )
		self._sendMsgPacket( BWLOCKCOMMAND_LOCK, rectStr + lockMsg )
		commandCode, failure, msg = self._waitForReply( BWLOCKCOMMAND_LOCK )
		if not failure:
			self._waitForReply( BWLOCKNOTIFY_LOCK )

	def unlock( self, rect, unlockMsg, failureOK = False ):
		log.debug( "UNLOCK command: %r, %s", rect, unlockMsg )
		rectStr = self.packRect( rect )
		self._sendMsgPacket( BWLOCKCOMMAND_UNLOCK, rectStr + unlockMsg )
		commandCode, failure, msg = self._waitForReply( BWLOCKCOMMAND_UNLOCK,
			failureOK )
		if not failure:
			self._waitForReply( BWLOCKNOTIFY_UNLOCK )

	def getStatus( self ):
		log.debug( "GETSTATUS command" )
		self._sendMsgPacket( BWLOCKCOMMAND_GETSTATUS )
		commandCode, failure, payload = \
			self._waitForReply( BWLOCKCOMMAND_GETSTATUS )

		if failure:
			raise ValueError, "getStatus returned failure: %s", payload

		computerName = None
		locks = {}
				# recordLen is unused

		log.debug( " ".join( ["%02x" % ch for ch in map( ord, payload )] ) )

		while payload:
			recordLen, payload = self._streamFormat( "I", payload )
			record, payload = self._streamSplit( recordLen, payload )

			computerNameLen, record = self._streamFormat( "I", record )
			computerName, record = self._streamSplit( computerNameLen, record )
			numLocks, record = self._streamFormat( "I", record )

			while numLocks:

				(left, top, right, bottom, usernameLen), record = \
					self._streamFormat( "hhhhI", record )
				rect = Rect( left, top, right, bottom )

				username, record = self._streamSplit( usernameLen, record )

				descLen, record = self._streamFormat( "I", record )
				desc, record = self._streamSplit( descLen, record )

				lockTimeFloat, record = self._streamFormat( "f", record )
				lockTime = datetime.datetime.fromtimestamp( lockTimeFloat )

				lockList = locks.setdefault( computerName, [] )
				lockList.append(
					Lock( rect, computerName, username, desc, lockTime ) )

				numLocks -= 1

		return locks



	def _waitForReply( self, expectedCommandCode=None, failureOK=False ):
		commandCode, failure, payload = self._recvReply()
		if expectedCommandCode != None and commandCode != expectedCommandCode:
			log.error( "Invalid command code for reply: '%s'",
				commandCode )
			raise ValueError, "Invalid command code for reply: '%s'" % \
				commandCode
		if failure and not failureOK:
			log.error( "Command failure" )
			raise ValueError, "Command failure"
		return commandCode, failure, payload


	def _sendMsgPacket( self, code, payload='', failure = False ):
		failureByte = 0
		if failure:
			failureByte = 1
		totalLen = struct.calcsize( "IcB" ) + len( payload )
		header = struct.pack( "IcB", totalLen, code, failureByte )
		self._socket.sendall( header + payload )

	@staticmethod
	def packRect( rect ):
		return struct.pack( "hhhh",
				rect.left, rect.top, rect.right, rect.bottom )

	def _recvUpTo( self, n ):
		if n == 0:
			return ''
		if self._socket is None:
			return None
		buffer = ""
		left = n
		chunk = self._socket.recv( left )
		while left and chunk != '':
			buffer += chunk
			left -= len( chunk )
			if left:
				chunk = self._socket.recv( left )
		if len( buffer ) != n:
			log.error( "Only received %d bytes", len( buffer ) )
			raise ValueError, "did not receive expected bytes (%d)" % n
		return buffer

	def _recvReply( self ):
		header = self._recvUpTo( struct.calcsize( "IcB" ) )
		if not header:
			# disconnected
			return False
		totalLen, commandCode, failureByte = struct.unpack( "IcB", header )
		payload = self._recvUpTo( totalLen - 6 )

		failure = bool( failureByte )

		if commandCode == BWLOCKCOMMAND_CONNECT:
			self._onSimpleReply( "CONNECT", failure, payload )
		elif commandCode == BWLOCKCOMMAND_SETUSER:
			self._onSimpleReply( "SETUSER", failure, payload )
		elif commandCode == BWLOCKCOMMAND_SETSPACE:
			self._onSimpleReply( "SETSPACE", failure, payload )
		elif commandCode == BWLOCKCOMMAND_LOCK:
			self._onSimpleReply( "LOCK", failure, payload )
		elif commandCode == BWLOCKCOMMAND_UNLOCK:
			self._onSimpleReply( "UNLOCK", failure, payload )
		elif commandCode == BWLOCKNOTIFY_LOCK:
			self._onLockNotify( "LOCK", failure, payload )
		elif commandCode == BWLOCKNOTIFY_UNLOCK:
			self._onLockNotify( "UNLOCK", failure, payload )
		elif commandCode == BWLOCKCOMMAND_GETSTATUS:
			self._onGetStatus( failure, payload )
		else:
			log.error( "unknown command code = '%s'", commandCode )
			self._disconnect( "unknown command code = '%s'" % commandCode )

		return commandCode, failureByte, payload

	def _onSimpleReply( self, commandName, failure, payload ):
		successString = "success"
		if failure:
			successString = "failed"
		log.info( "%s reply %s: %s", commandName, successString, payload )

	def _onLockNotify( self, lockOp, failure, payload ):
		(left, top, right, bottom, computerNameLen), payload = \
			self._streamFormat( 'hhhhI', payload )

		computerName, payload = self._streamSplit( computerNameLen, payload )
		usernameLen, payload = self._streamFormat( "I", payload )
		username, payload = self._streamSplit( usernameLen, payload )
		descLen, payload = self._streamFormat( "I", payload )
		desc, payload = self._streamSplit( descLen, payload )
		lockTimeFloat, payload = self._streamFormat( "f", payload )

		rect = Rect( left, top, right, bottom )
		lockTime = datetime.datetime.fromtimestamp( lockTimeFloat )
		if payload:
			log.warning( "Extra %d bytes at the end of LOCK notification message",
				len( payload ) )

		if failure:
			log.error( "Got lock state notification with failure signal" )
			raise ValueError, "Got lock state notification with failure signal"
		log.info( "%s notification: %r by %s@%s at %s: %s",
			lockOp, rect, username, computerName, lockTime.strftime( "%c" ),
			desc )

	def _onGetStatus( self, failure, payload ):
		if failure:
			raise ValueError, payload

		log.info( "GETSTATUS reply success" )

	def _handleFailure( self, failure, commandDesc ):
		if failure:
			log.error( "%s reply has failure byte, disconnecting", commandDesc )
			self._disconnect( "%s reply has failure" % commandDesc )

	@staticmethod
	def _streamFormat( structFormat, payload ):
		formatLen = struct.calcsize( structFormat )
		data, tail = BWLockDConnection._streamSplit( formatLen, payload )
		unpacked = struct.unpack( structFormat, data )
		if len( unpacked ) == 1:
			unpacked = unpacked[0]

		return unpacked, tail

	@staticmethod
	def _streamSplit( numBytes, payload ):
		return payload[:numBytes], payload[numBytes:]

	def disconnect( self ):
		self._disconnect()

	def _disconnect( self, reason = None ):
		if self._socket == None:
			log.warning( "Already disconnected" )
			return

		self._socket.close()
		self._socket = None
		if reason:
			raise ValueError, reason
		log.info( "Disconnecting" )


def main( host, port ):
	log.info( "BWLockDTest starting" )
	conn1 = BWLockDConnection()

	conn1.connect( host, port )

	try:
		conn1.username( "client1" )
		conn1.setSpace( "spaces/test" )

		outerRect = Rect( 5, 5, 10, 10 )
		innerRect = Rect( 8, 8, 9, 9 )

		outerRect2 = Rect( 11, 11, 15, 15 )

		conn1.unlock( outerRect, "test", failureOK=True )

		conn1.lock( outerRect, "test" )

		locks = conn1.getStatus()
		if locks:
			log.info( "Locks held: \n%s",
				"\n".join(
					["%r %s" % (lock.rect, lock.lockTime.strftime( "%c" ))
						for lock in locks[socket.gethostname()]]
				) )

		# get rid of all our locks
		for computerName, locks in locks.items():
			if computerName == socket.gethostname():
				for lock in locks:
					conn1.unlock( lock.rect, "test" )
	finally:
		conn1.disconnect()

	log.info( "BWLockDTest finishing" )

if __name__ == "__main__":
	import sys

	logging.basicConfig( level=logging.DEBUG, format=LOG_FORMAT )

	if len( sys.argv ) < 2:
		print "usage: %s host [port]" % sys.argv[0]
		sys.exit( 1 )
	host = sys.argv[1]

	port = 8168
	if len( sys.argv ) >= 3:
		port = int( sys.argv[2] )

	main( host, port )

