from datetime import timedelta

from bwtest import config
from template_reader import TemplateReader
from helpers.cluster import ClusterController

class TestCommon( object ):

	
	ARCHIVE_PERIOD = 5
	NEEDED_CONFIGS = {"baseApp/archivePeriod": str( ARCHIVE_PERIOD )}
	RES_TREE = [ "simple_space/res" ]
	
	def setUp( self ):
		self._cc = ClusterController( self.RES_TREE )
		for path, value in self.NEEDED_CONFIGS.items():
			self._cc.setConfig( path, value )
		xmlPath = config.TEST_ROOT + "/tests/watchers/layout.xml"
		self._cc.start(
			layoutXML = TemplateReader( xmlPath, machine=self._cc._machines[0] ) )
		self._cc.waitForServerSettle()


	def tearDown( self ):
		self._cc.stop()
		self._cc.clean()

	def compareDates( self, date1, date2 ):
		ret = date1 - date2 < timedelta( seconds = 60 )
		return ret
	
	def convertToSeconds( self, uptime):
		parts = uptime.split()
		seconds = int( parts[-2] )
		minutes =  0
		if len( parts ) > 2:
			int( parts[-4] )
		hours = 0
		if len( parts ) > 4:
			int( parts[-6] )
		return hours*3600 + minutes*60 + seconds
	
	def isPowerOfTwo( self, num ):
		return num != 0 and ((num & (num - 1)) == 0)
	
	def isPrime( self, n ):
		'''check if integer n is a prime'''
		# make sure n is a positive integer
		n = abs(int(n))
		# 0 and 1 are not primes
		if n < 2:
			return False
		# 2 is the only even prime number
		if n == 2: 
			return True    
		# all other even numbers are not primes
		if not n & 1: 
			return False
		# range starts with 3 and only needs to go up the squareroot of n
		# for all odd numbers
		for x in range(3, int(n**0.5)+1, 2):
			if n % x == 0:
				return False
		return True
