#!/usr/bin/env python

import sys
import os
import platform
import re

class TestEncryption( object ):

	def __init__( self ):

		# The key that res_packer should be compiled with
		self.srcKey = None
		self.key = None

		# Temporary file we'll encrypt
		self.test_file = "test_file.txt"

		# Temporary encrypted file
		self.enc_file  = "test_file.enc"

		self.bw_res = os.path.abspath("../../../../res/bigworld")
		self.fd_res = os.path.abspath("../../../../res/fantasydemo")

		
		arch = ""
		if platform.machine() == "x86_64":
			arch = "64"
		self.res_packer = os.path.abspath(
			os.path.curdir + "/../../server/bin/Hybrid%s/res_packer" % arch )


	def __del__( self ):
		if os.path.isfile( self.test_file ):
			os.remove( self.test_file )
		if os.path.isfile( self.enc_file ):
			os.remove( self.enc_file )
		return

	def getSrcKey( self ):

		KEY_FILE = "../../../../../programming/bigworld/lib/resmgr/packed_section.cpp"
		KEY_LINE = "const char BW_ENCRYPTION_KEY = char(0x"

		fp = open( KEY_FILE )
		for line in fp.xreadlines():
			if line.startswith( KEY_LINE ):
				break

		fp.close()

		m = re.match( ".*char\(0x(?P<key>[a-f0-9]+)\);", line )
		if m != None:
			self.srcKey = m.group( "key" )

		else:
			print "******************"
			print "UNABLE TO FIND KEY IN", KEY_FILE
			print "******************"
			sys.exit( 1 )

		return

	def encrypt( self ):
		os.system( "%s --res %s:%s --encrypt %s %s > /dev/null" %
			(self.res_packer, self.fd_res, self.bw_res,
				os.path.abspath( self.test_file ),
				os.path.abspath( self.enc_file )) )
		return

	def getEncryptedKey( self ):

		# XXX: Note the magic number here. Due to the overhead of the
		#      packed section data (13 byte header we seek to byte 14),
		#      this may change in the future and is a likely candidate
		#      for being fixed.
		PACKED_HEADER_SIZE = 13
		fp = open( self.enc_file )
		fp.seek( PACKED_HEADER_SIZE )
		encChar = fp.read( 1 )
		fp.close()

		fp = open( self.test_file )
		txtChar = fp.read( 1 )
		fp.close()

		key = ord( encChar ) ^ ord( txtChar )
		#print "Enc:", hex( ord( encChar ) )
		#print "Txt:", hex( ord( txtChar ) )
		#print "Key:", hex( key )

		return key

	def run( self ):
		if not os.path.isfile( self.res_packer ):
			print "ResPacker not found at:", self.res_packer
			return 1


		self.getSrcKey()

		# Convert the key into something more useable
		self.key = int( self.srcKey, 16 )


		# Write out the test file
		fp = open( self.test_file, "w" )
		fp.write( "This line is a test\n" )
		fp.close()

		# Now encrypt our test file
		self.encrypt()

		encKey = self.getEncryptedKey()

		status = 0
		if encKey != self.key:
			status = 1
			print
			print "*********************"
			print "RES_PACKER KEY ERROR"
			print
			print "Key in binary:", hex( encKey )
			print "Key in source:", hex( self.key )
			print "*********************"

		return status


# Ensure we run from the directory where the script is located
os.chdir( os.path.dirname( os.path.abspath( sys.argv[0] ) ) )
test = TestEncryption()
sys.exit( test.run() )
