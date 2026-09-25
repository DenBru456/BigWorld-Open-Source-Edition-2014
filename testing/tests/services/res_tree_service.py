import time
import os
import subprocess

from helpers.cluster import ClusterController
from helpers.command import Command, remove

from bwtest import log, TestCase

servePath = 'res/scripts/server_data/space_viewer_images'
#fileName = 'Avatar.png'
fileName = 'duramare.png'
filePath = servePath + '/' + fileName

class TestFileServing( TestCase ):
	name = "File serving test" 
	description = "Test the ResTreeService to serve files fully" \
		" and without corruption." 
	 #Test only serves a purpose in -r mode to reproduce failure in BWT-21601
	tags = [ 'MANUAL' ]

	serviceIp = None
	servicePort = None

	commands = []

	def _runMultiple( self, command ):
		log.debug( "Running command '%s'" % command )
		self.commands.append( command )


	def step0( self ):
		self.cc_ = ClusterController( ["simple_space_with_services/res",
											  "simple_space/res"] )
		self.cc_.start()


	def step1( self ):
		"""Get ResTreeService port to connect to"""

		numTries = 0
		while numTries < 5:
			serviceAddress = self.cc_.getWatcherValue( 
				"services/HTTPResTreeService/address", 'serviceapp' )
			if serviceAddress:
				break
			numTries += 1

		self.assertTrue( serviceAddress is not None, 
			"Could not fetch ResTreeService address." )

		log.debug( "serviceAddress is '%s'" % serviceAddress )
		self.serviceIp, self.servicePort = serviceAddress.split( ':' )
		log.debug( "ResTreeService can be reached at: %s:%s" % \
			(self.serviceIp, self.servicePort) )


	def step3( self ):
		"""Loop for 20 times and fetch the file, check length and checksum
	       against initial values"""

		self.commands = []
		pattern = fileName
		pattern.replace( " ", "" )
		
		remove( "/tmp/%s.*" % pattern )

		for step in range( 20 ):
			self._runMultiple( 
				"wget --directory-prefix=/tmp --tries=3 http://%s:%s/%s" % \
				(self.serviceIp, self.servicePort, filePath) ) 

		cmd = Command( self.commands )
		cmd.call( parallel = True )


		(_, _, filenames) = os.walk( "/tmp" ).next()
		foundFiles = [ f for f in filenames if f.find( pattern ) >= 0 ]
		log.debug( "found files: %s" % foundFiles )

		lastSize = None
		lastFile = None
		cmd = Command()
		for file in foundFiles:
			size = os.path.getsize( "/tmp/" + file )
			if lastSize:
				log.debug( "size of %s is %r" % (file, size) )
				self.assertTrue( size == lastSize, 
					"Size check failed! Last size = %r, cur size = %r" % \
					(lastSize, size) )
				diffResult = cmd.call( "-diff %s %s" % \
							("/tmp/"+file, "/tmp/"+lastFile) 
						)
				self.assertTrue( diffResult == True,
					"File contents differ between %s and %s!" % \
					(file, lastFile) )
			lastFile = file
			lastSize = size
		
		pattern.replace( " ", "" )
		remove( "/tmp/%s.*" % pattern )

	def tearDown( self ):
		self.cc_.stop()
		self.cc_.clean()


